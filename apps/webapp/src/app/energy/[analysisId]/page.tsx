import { getEnergyByTimeSlot } from '@/actions/energy-form'
import DataTable from '@/components/ui/data-table'

const EnergyAnalysisPage = async ({ params }: { params: { analysisId: string } }) => {
  const data = await getEnergyByTimeSlot(params.analysisId)

  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl mb-6">Energy</h1>
      <DataTable data={data} />
    </main>
  )
}
export default EnergyAnalysisPage
