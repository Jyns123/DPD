import InmoScoreApp from '../../components/inmoscore-app';
import { getListings } from '../../lib/catalog';
export const dynamic = 'force-dynamic';
export default function Page() { return <InmoScoreApp listingCount={getListings().length} />; }
