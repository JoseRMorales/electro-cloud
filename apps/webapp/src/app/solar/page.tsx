import AnalysisCardGrid from '@/components/analysis-card-grid'
import SolarForm from '@/components/solar-form'

const SolarPage = () => {
  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl">Solar</h1>
      <SolarForm />
      <AnalysisCardGrid api="solar" />
    </main>
  )
}
export default SolarPage
