import { getEnergyByTimeSlot } from '@/actions/energy-form'
import DataTable from '@/components/ui/data-table'

const EnergyAnalysisPage = async ({
  params
}: {
  params: Promise<{ analysisId: string }>
}) => {
  const { analysisId } = await params
  const data = await getEnergyByTimeSlot(analysisId)

  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl mb-6">Energy</h1>
      <DataTable data={data} />
    </main>
  )
}
export default EnergyAnalysisPage
