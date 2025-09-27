import { Dashboard } from "@/components/dashboard";

interface PageProps {
  params: {
    id: string;
  };
}

export default function HouseholdPage({ params }: PageProps) {
  return <Dashboard householdId={params.id} />;
}