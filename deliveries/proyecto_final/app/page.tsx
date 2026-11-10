import InmoScoreApp from '../components/inmoscore-app';
import { getListings } from '../lib/catalog';
export default function Page() { return <InmoScoreApp listingCount={getListings().length} />; }
