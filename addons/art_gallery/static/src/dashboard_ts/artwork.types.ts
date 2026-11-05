export interface Artwork {
  id: number;
  name: string;
  artist_name: string;
  year: number | null;
  image: string | null;
}

export function fetchArtworks(): Promise<Artwork[]> {
  // Más adelante reemplazarás esto por la llamada real al ORM de Odoo
  return Promise.resolve([]);
}