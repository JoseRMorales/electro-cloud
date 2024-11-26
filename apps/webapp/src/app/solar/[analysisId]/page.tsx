import {
  getSolarConsumptionProductionPlot,
  getSolarMonthlyConsumption,
  getSolarMonthlyPlots,
  getSolarMonthlyProduction,
  getSolarSelfPercentRatios
} from '@/actions/solar-form'
import DataTable from '@/components/ui/data-table'
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'

const EnergyAnalysisPage = async ({
  params
}: {
  params: Promise<{ analysisId: string }>
}) => {
  const { analysisId } = await params
  const plot1 = await getSolarConsumptionProductionPlot(analysisId)
  const monthlyPlots = await getSolarMonthlyPlots(analysisId)
  const { monthly_ratios, average } =
    await getSolarSelfPercentRatios(analysisId)
  const monthly_production = await getSolarMonthlyProduction(analysisId)
  const monthly_consumption = await getSolarMonthlyConsumption(analysisId)

  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl mb-6">Solar</h1>
      <h2 className="text-3xl mb-6">Consumption vs Production Chart</h2>
      <img src={plot1} />
      <h2 className="text-3xl mb-6">Month analysis</h2>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
          gap: '16px'
        }}
      >
        {monthlyPlots.map((src, index) => (
          <img
            key={index}
            src={src}
            alt={`Solar Plot ${index + 1}`}
            style={{ width: '100%', height: 'auto' }}
          />
        ))}
      </div>
      <h2 className="text-3xl mb-6">Self Consumption Percent Ratios</h2>
      <div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Month</TableHead>
              <TableHead className="text-right">Ratio</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {monthly_ratios.map((ratio, index) => (
              <TableRow key={index}>
                <TableCell>{index}</TableCell>
                <TableCell className="text-right">{ratio}</TableCell>
              </TableRow>
            ))}
          </TableBody>
          <TableFooter>
            <TableRow>
              <TableCell colSpan={1}>Average</TableCell>
              <TableCell className="text-right">{average}</TableCell>
            </TableRow>
          </TableFooter>
        </Table>
      </div>
      <h2 className="text-3xl mb-6">Monthly Production</h2>
      <div className="max-w-sm">
        <DataTable data={monthly_production} clipboard={false} />
      </div>
      <h2 className="text-3xl mb-6">Monthly Consumption</h2>
      <div className="max-w-sm">
        <DataTable data={monthly_consumption} clipboard={false} />
      </div>
    </main>
  )
}
export default EnergyAnalysisPage
