# Auditoría técnica del workspace

## Resumen

El proyecto contiene tres módulos instalables bajo `addons/` para Odoo 19:

- `art_gallery`: catálogo de obras, gestión de artistas, importación desde la API del Art Institute of Chicago y dashboards OWL.
- `art_marketplace`: publicación de obras, solicitudes públicas, seguimiento de tickets, venta y facturación.
- `art_app_launcher`: lanzador visual OWL de aplicaciones del backend.

Esta auditoría describe el código actual. Cuando una regla esperada no está implementada o difiere de la intención funcional, se señala expresamente como observación.

## 1. Módulo `art_gallery`

### Configuración

El manifiesto declara la versión `19.0.1.0.1`, como aplicación instalable, con dependencia de:

- `base`
- `web`
- Paquete Python `requests`

Carga permisos, el wizard de importación, las vistas de artistas y obras, los dos dashboards y los menús. Sus assets de backend incluyen CSS, JavaScript y plantillas OWL.

### Modelo `art_gallery.artist`

Representa al artista como entidad propia.

| Campo | Tipo | Comportamiento |
|---|---|---|
| `name` | `Char`, requerido | Nombre del artista. |
| `email` | `Char` | Email sincronizado con el contacto. |
| `biography` | `Text` | Biografía o descripción. |
| `commission_percentage` | `Float`, por defecto `50.0` | Porcentaje del precio reservado para el artista. |
| `active` | `Boolean`, por defecto `True` | Permite archivar artistas. |
| `partner_id` | `Many2one` a `res.partner` | Contacto asociado, con `ondelete='restrict'`. |
| `artwork_ids` | `One2many` a `art_gallery.artwork` | Obras relacionadas mediante `artist_id`. |
| `artwork_count` | `Integer`, calculado y almacenado | Cantidad de obras relacionadas. |

La relación principal es:

```text
Artista (1) ───── (N) Obras
```

`artwork_ids` usa `inverse_name='artist_id'`, por lo que cada obra guarda la referencia física al artista.

El modelo:

- ordena los artistas por cantidad de obras descendente y después por nombre;
- crea un contacto `res.partner` automáticamente cuando se crea un artista sin `partner_id`;
- sincroniza los cambios de `name` y `email` hacia el contacto asociado;
- ofrece `_get_or_create_partner()`, que crea el contacto sólo si ese artista todavía no tiene uno;
- ofrece `action_view_artworks()`, que abre las obras del artista.

Las vistas permiten listar, buscar, archivar, editar artistas y abrir sus obras mediante un botón estadístico.

### Modelo `art_gallery.artwork`

Representa una obra importada o registrada manualmente.

| Campo | Tipo | Observación |
|---|---|---|
| `name` | `Char`, requerido | Título. |
| `artist_id` | `Many2one` a `art_gallery.artist` | Relación principal con el artista; `ondelete='restrict'`. |
| `artist_name` | `Char` | Nombre legado/importado, mantenido por compatibilidad. |
| `artist_display` | `Char` | Texto ampliado del artista devuelto por la API, mantenido por compatibilidad. |
| `description` | `Text` | Descripción. |
| `external_id` | `Char`, indexado | Identificador del catálogo externo. |
| `image` | `Binary`, adjunto | Imagen local descargada. |
| `image_url` | `Char` | URL de origen. |
| `year` | `Integer` | Año. |

`artist_name` y `artist_display` siguen presentes, pero la relación funcional y las nuevas ventas utilizan `artist_id`.

La restricción Odoo 19 `UNIQUE(external_id)` impide que dos obras compartan el mismo identificador externo cuando éste tiene valor.

### Importación desde la API

`action_import_artworks(year_from=None, year_to=None, limit=10)`:

1. Consulta `https://api.artic.edu/api/v1/artworks/search`.
2. Solicita `id`, `title`, `artist_title`, `artist_display`, `image_id` y `date_start`.
3. Añade filtros opcionales por rango de años.
4. Omite cualquier obra cuyo `external_id` ya exista.
5. Busca un artista por nombre exacto, incluyendo artistas archivados mediante `active_test=False`.
6. Crea el artista si no lo encuentra.
7. Garantiza que el artista tenga `partner_id`.
8. Descarga la imagen desde IIIF cuando existe `image_id`.
9. Crea la obra conservando `artist_id`, `artist_name` y `artist_display`.

Los errores de la petición principal se registran en el log y devuelven `False`. El fallo al descargar una imagen se registra y no impide crear la obra.

El método usa por defecto `limit=10`, y el wizard de importación usa `5` como valor predeterminado.

**Límite de 100:** actualmente no hay una validación en el modelo ni en el wizard que limite a 100 el parámetro enviado a la API. `limit` puede recibirse con otro valor y se copia a los parámetros de la petición. Por tanto, un máximo de 100 no está implementado como regla local del proyecto. Si el servicio externo impone ese límite, la aplicación depende del comportamiento de la API y debería añadir una validación explícita `1 <= limit <= 100`.

### Dashboards

- `get_gallery_data(offset=0, limit=10)` entrega total y página ordenada por ID descendente.
- `get_dashboard_data(year_from=None, year_to=None)` valida que los años sean enteros, filtra por año, ordena y devuelve hasta 50 obras.
- El dashboard JavaScript incluye paginación.
- El dashboard TypeScript/JavaScript ofrece filtros de año y validación de rangos.

### Wizard de importación

`art_gallery.import_wizard` es transitorio y solicita año inicial, año final y cantidad. `action_confirm_import()` delega en `action_import_artworks()` y cierra el modal.

### Permisos y vistas

Los usuarios internos (`base.group_user`) tienen lectura, escritura, creación y eliminación sobre artistas, obras y wizard de importación.

Las vistas incluyen listas, kanban, formularios, búsquedas, filtros de artistas archivados o con más de cinco obras, botones de importación y menús `Artworks`, `Artists`, `Gallery Dashboard` y `Dashboard (TS)`.

## 2. Módulo `art_marketplace`

### Configuración

El manifiesto declara versión `19.0.1.0.0` y depende de:

- `base`
- `art_gallery`
- `account`
- `website`
- `phone_validation`

El módulo es instalable como aplicación y carga permisos, ventas, tickets, wizard, menús y plantillas web.

### Modelo `art_marketplace.artwork_sale`

Representa la oferta y el ciclo de venta de una obra.

| Campo | Tipo | Comportamiento |
|---|---|---|
| `purchase_request_ids` | `One2many` a `art_marketplace.purchase_request` | Tickets asociados mediante `artwork_sale_id`. |
| `purchase_request_count` | `Integer`, calculado | Cantidad de tickets. |
| `company_id` | `Many2one` requerido | Compañía activa por defecto. |
| `currency_id` | `Many2one` requerido | Moneda de la compañía por defecto. |
| `description` | `Text` | Notas de la venta. |
| `artwork_image` | `Binary` relacionado | Imagen de `artwork_id`, solo lectura. |
| `artist_id` | `Many2one`, requerido | Artista utilizado para filtrar obras. |
| `artwork_id` | `Many2one`, requerido e indexado | Obra ofrecida. |
| `price` | `Monetary` | Precio de venta. |
| `artist_commission_percentage` | `Float` relacionado | Se obtiene de `artwork_id.artist_id.commission_percentage`. |
| `artist_commission_amount` | `Monetary`, calculado | `price * comisión / 100`. |
| `gallery_net_income` | `Monetary`, calculado | `price - comisión del artista`. |
| `state` | `Selection`, requerido | `draft`, `published`, `sold`. |
| `seller_id` | `Many2one`, requerido | Partner del usuario por defecto. |
| `buyer_id` | `Many2one` | Comprador final. |
| `sale_date` | `Date` | Fecha de venta. |
| `invoice_id` | `Many2one` a `account.move` | Factura de cliente. |
| `artist_invoice_id` | `Many2one` a `account.move` | Factura de proveedor del artista. |
| `active_artwork_id` | `Many2one` calculado/almacenado | Auxiliar de unicidad. |
| `unavailable_artwork_ids` | `Many2many` calculado | Obras no disponibles para selección en la UI. |

Los `onchange` mantienen coherencia entre artista y obra:

- cambiar el artista limpia una obra que no pertenezca a ese artista;
- cambiar la obra asigna su artista y, si está vacía, copia su descripción;
- el dominio de `artwork_id` limita por artista y por la lista de obras disponibles.

`active_artwork_id` contiene la obra mientras la venta no está en `sold`. La restricción SQL `UNIQUE(active_artwork_id)` evita dos ventas activas para la misma obra.

Separadamente, `_compute_unavailable_artwork_ids()` incluye todas las obras que aparecen en cualquier venta, incluso vendidas. Por ello la interfaz es más restrictiva que la regla SQL: normalmente impide seleccionar desde la UI una obra ya utilizada, aunque una venta `sold` haya liberado `active_artwork_id`.

### Comisiones y doble facturación

Los importes de comisión se recalculan cuando cambian precio o porcentaje:

```text
artist_commission_amount = price * artist_commission_percentage / 100
gallery_net_income = price - artist_commission_amount
```

El porcentaje corresponde al artista relacionado con la obra. No existe actualmente una restricción entre 0 y 100, por lo que ese rango debería validarse si es una regla obligatoria.

Al ejecutar `action_sell(buyer_id=None)` sobre ventas en `published`:

1. La venta pasa a `sold` y recibe la fecha actual.
2. Si se proporcionó comprador, se guarda en `buyer_id`.
3. Si no existe comprador, la venta queda `sold`, pero su iteración de facturación se omite.
4. Con comprador, se crea una **Factura de Cliente (`out_invoice`) por el 100% del precio** y se guarda en `invoice_id`.
5. Si la obra tiene un artista con contacto y su comisión es mayor que cero, se crea una **Factura de Proveedor (`in_invoice`) por la comisión** y se guarda en `artist_invoice_id`.
6. Los documentos se crean usando la compañía de la venta.
7. Al terminar, todos los tickets relacionados en `new` o `contacted` pasan a `won`; si un ticket no tiene partner, recibe el comprador de la venta.

Las dos facturas se crean en estado inicial de Odoo, no se registran ni pagan automáticamente.

La reversión `action_reset_to_published()`:

- combina las dos facturas;
- impide la reversión si alguna ya no está en borrador;
- elimina las facturas que permanecen en borrador;
- limpia comprador, fecha, factura de cliente y factura de artista;
- devuelve la venta a `published`.

Los tickets ganados por una venta no se reabren durante esta reversión.

### Relación entre venta y tickets

Cada ticket tiene:

```python
artwork_sale_id = fields.Many2one(
    'art_marketplace.artwork_sale',
    required=True,
)
```

La venta tiene la relación inversa:

```python
purchase_request_ids = fields.One2many(
    'art_marketplace.purchase_request',
    inverse_name='artwork_sale_id',
)
```

Por tanto:

```text
Venta (1) ───── (N) Purchase Request
```

El campo `artwork_sale_id` en el ticket se persiste con el ID de la venta. El `domain` del campo exige una venta `published` al seleccionarla desde la interfaz.

### Modelo `art_marketplace.purchase_request`

| Campo | Tipo | Comportamiento |
|---|---|---|
| `name` | `Char`, solo lectura | Referencia, por defecto `Nuevo`. |
| `artwork_sale_id` | `Many2one`, requerido e indexado | Venta asociada. |
| `partner_id` | `Many2one` a `res.partner` | Contacto asociado. |
| `customer_name` | `Char`, requerido | Nombre indicado por el visitante. |
| `customer_email` | `Char`, requerido | Email indicado por el visitante. |
| `customer_phone` | `Char` | Teléfono. |
| `message` | `Text` | Consulta. |
| `state` | `Selection`, requerido | `new`, `contacted`, `won`, `canceled`. |
| `request_date` | `Date`, requerido | Fecha actual por defecto. |

#### Prevención de contactos duplicados

`_find_or_create_partner()` aplica la política para compradores:

1. Reutiliza `partner_id` si el ticket ya tiene uno.
2. Busca un contacto con el mismo email exacto.
3. Si no existe y hay teléfono, busca por nombre y teléfono exactos.
4. Sólo crea un contacto nuevo si ninguna coincidencia es válida.
5. Asigna el contacto resultante al ticket.

Esta lógica evita fusionar de forma insegura a dos personas homónimas con email o teléfono distintos. El email es el identificador preferido; nombre más teléfono es la alternativa.

No existe una restricción SQL global de unicidad para el email en `res.partner`, ni una transacción de deduplicación para operaciones concurrentes. Por ello reduce duplicados, pero no garantiza deduplicación absoluta frente a dos creaciones simultáneas.

Esta política pertenece al flujo de tickets/compradores. El `create()` de `art_gallery.artist` todavía crea un contacto sin buscar primero uno equivalente, por lo que no debe considerarse una deduplicación universal de todos los contactos.

#### `action_mark_contacted()`

- Sólo acepta tickets en `new`.
- Resuelve o crea el contacto mediante `_find_or_create_partner()`.
- Pasa el ticket a `contacted`.
- Si se opera sobre varios tickets, un ticket con estado incorrecto produce `UserError`.

#### `action_win_ticket()`

- Sólo acepta un ticket en `new` o `contacted` a nivel Python.
- Rechaza cerrar un ticket cuya venta ya está `sold`.
- Resuelve o crea el contacto, incluso si el ticket saltó `contacted`.
- Asigna ese partner como comprador.
- Invoca `sale.action_sell(buyer_id=partner)`.
- Pasa explícitamente el ticket a `won`.

La vista actual sólo muestra el botón `Win Ticket` para `contacted`. La aceptación de `new` existe en el método, pero no está expuesta por ese botón.

#### `action_cancel_ticket()`

- No permite cancelar un ticket `won`.
- Si el partner del ticket era el comprador previsto y la venta aún no está vendida, limpia el comprador y vuelve la venta a `published`.
- Marca el ticket como `canceled`.

### Wizard `art_marketplace.sell_wizard`

El wizard es un `TransientModel` con:

- `sale_id`: venta requerida y de solo lectura.
- `buyer_id`: comprador requerido.
- `valid_buyer_ids`: Many2many calculado de `res.partner`.

`_compute_valid_buyer_ids()` busca tickets de la venta actual que cumplan:

- estado `contacted`;
- `partner_id` informado.

Los partners obtenidos se asignan a `valid_buyer_ids`. La vista aplica:

```xml
domain="[('id', 'in', valid_buyer_ids)]"
```

Por tanto, el dominio de `buyer_id` es dinámico respecto de `sale_id`, pero **la implementación actual sólo admite `contacted`**, no tickets `new`. Esta decisión coincide con el botón visible de venta del ticket, que también se muestra para `contacted`.

`action_confirm_sale()` llama a `sale.action_sell(buyer_id=self.buyer_id)` y cierra el modal.

### Vistas y sitio público

- El formulario de venta muestra publicación, wizard de venta, reversión, estado, imagen, comisiones y facturas.
- Existe un botón estadístico para abrir los tickets y una alerta cuando hay solicitudes.
- Las búsquedas y listas ofrecen filtros y badges por estado.
- El vendedor y el comprador se limitan en la vista a contactos que no son compañías; este dominio no forma parte de una restricción del modelo.
- `/gallery` muestra únicamente ventas `published`.
- `/gallery/request/<sale_id>` acepta GET/POST y verifica que la venta exista y siga publicada.
- El POST crea el ticket mediante `sudo`, con estado inicial `new`.
- El teléfono se normaliza/intenta validar con `phone_validation`; como alternativa se acepta un patrón internacional `+\d{7,20}`.
- Las plantillas incluyen catálogo, formulario de interés y página de agradecimiento.

### Permisos

Los usuarios internos (`base.group_user`) tienen lectura, escritura, creación y eliminación sobre ventas, tickets y wizard.

La creación pública de tickets funciona mediante `sudo` en el controlador; no se han añadido reglas de registro (`ir.rule`) específicas en el módulo.

### Extensión de `res.partner`

`art_marketplace.models.res_partner` extiende `_compute_display_name()`. Cuando el contexto contiene `show_only_name`, muestra sólo el nombre de contactos que son personas con empresa padre.

## 3. Módulo `art_app_launcher`

Depende de `base` y `web`. No está marcado como aplicación principal.

### Modelo `ir.ui.menu`

Hereda sin añadir campos persistentes. `get_app_launcher_data()`:

1. Busca los menús raíz ordenados por secuencia e ID.
2. Usa la acción del menú raíz o la del primer hijo que tenga acción.
3. Devuelve aplicaciones que tengan `web_icon` o acción, con `id`, `name`, `action` e `icon`.

### Componentes OWL

- `AppLauncher`: acción cliente registrada como `art_app_launcher`; carga los datos por ORM RPC y muestra una grilla responsive de aplicaciones.
- Los iconos pueden ser data URI, rutas absolutas, formato `módulo,ruta` o valor directo. Sin icono utiliza un icono genérico.
- `HomeSystray`: agrega al systray un botón de inicio que abre `art_app_launcher.action_art_app_launcher`.

No hay controladores HTTP ni modelos persistentes propios.

## 4. Flujo completo de datos

1. Se importa o registra una obra y se vincula a un artista.
2. El artista tiene opcionalmente email, biografía y porcentaje de comisión; al crearse normalmente recibe un contacto.
3. Se crea una `artwork_sale`, se seleccionan artista, obra, precio y vendedor.
4. `action_publish()` cambia una venta `draft` a `published`.
5. La venta se muestra públicamente en `/gallery`.
6. El visitante envía una solicitud; se crea un ticket `new` asociado mediante `artwork_sale_id`.
7. `action_mark_contacted()` busca o crea el contacto del comprador y cambia el ticket a `contacted`.
8. La venta puede cerrarse:
   - desde el ticket mediante `action_win_ticket()`, o
   - desde el formulario de venta mediante `sell_wizard`.
9. El wizard sólo lista contactos de tickets `contacted` asociados a esa venta.
10. `action_sell()` marca la venta como vendida, fija comprador/fecha y crea las facturas de cliente y artista cuando corresponde.
11. Todos los tickets `new` o `contacted` de las ventas procesadas pasan a `won`, completando el ciclo desde cualquiera de los dos puntos de entrada.
12. Las facturas permanecen en borrador hasta que un proceso contable posterior las registre o pague.

## 5. Reglas de negocio y restricciones reales

- Un artista no puede borrarse si existen obras que apunten a él: `artwork.artist_id` usa `ondelete='restrict'`.
- Un `res.partner` asignado al artista tampoco puede borrarse mientras el artista lo tenga relacionado, porque `artist.partner_id` también usa `restrict`.
- La unicidad de `external_id` evita reimportar la misma obra.
- El importador reutiliza un artista existente por nombre exacto, pero no garantiza unicidad bajo variaciones del nombre ni operaciones concurrentes.
- Una obra sólo puede tener una venta activa por la restricción única de `active_artwork_id`.
- La UI considera indisponibles todas las obras que ya aparecen en una venta, incluidas las vendidas.
- Sólo una venta `draft` se publica desde `action_publish()`.
- `action_sell()` sólo procesa ventas `published`.
- El catálogo público y el formulario sólo trabajan con ventas `published`.
- El comprador del wizard sólo puede provenir de tickets `contacted` con partner.
- Los tickets nuevos pueden marcarse como contactados; sólo tickets `new`/`contacted` son elegibles para venta a nivel de método.
- Un ticket `won` no puede cancelarse.
- Al vender, todos los tickets abiertos de la misma venta pasan a `won`, incluidos otros tickets que representen clientes distintos.
- Los compradores se reutilizan por email exacto y, como alternativa, por nombre más teléfono exactos.
- La deduplicación de compradores no equivale a una deduplicación total de `res.partner`.
- No existe hoy una restricción de porcentaje entre 0 y 100.
- No existe hoy una validación local que limite la importación API a 100 elementos.
- Una venta sólo puede volver a `published` mientras sus dos facturas estén en borrador; si existen facturas registradas se rechaza la operación.

## 6. Riesgos y mejoras recomendadas

1. Añadir una validación explícita al límite API: por ejemplo, `1 <= limit <= 100`.
2. Añadir restricciones para `commission_percentage` entre 0 y 100.
3. Unificar la deduplicación de contactos de artistas y compradores mediante un servicio común.
4. Considerar normalización de emails y teléfonos antes de buscar contactos.
5. Valorar una restricción o índice condicional por email si la estrategia de datos lo permite; `res.partner` puede admitir escenarios legítimos más complejos.
6. Revisar que cerrar todos los tickets abiertos como `won` sea correcto cuando una obra recibe varios compradores potenciales.
7. Definir el estado de los tickets al revertir una venta: actualmente permanecen `won`.
8. Impedir a nivel de modelo asignar compradores no procedentes de un ticket elegible, no sólo mediante el dominio del wizard.
9. Hacer que `action_sell()` devuelva un error si una venta publicada carece de comprador, en vez de marcarla `sold` sin facturar.
10. Añadir pruebas automáticas Odoo para doble facturación, comisiones, deduplicación, cierre y reversión de tickets, dominio del wizard e importación.

## 7. Actores

- **Galerista / usuario interno**: administra artistas, importa obras, crea y publica ventas, procesa tickets y confirma ventas.
- **Visitante público**: consulta el catálogo y envía solicitudes.
- **Comprador (`res.partner`)**: contacto asociado al ticket, venta y factura de cliente.
- **Artista**: entidad que agrupa obras, porcentaje de comisión y contacto proveedor.
- **Vendedor (`res.partner`)**: partner del usuario creador de la venta, utilizado como dato de la oferta.
- **Contabilidad**: almacena las facturas de cliente y proveedor creadas durante la venta.
- **Art Institute of Chicago API**: fuente pública de catálogo e imágenes.
