import AnalysisCardGrid from '@/components/analysis-card-grid'
import FileUploadForm from '@/components/file-upload-form'

// To avoid errors in prerendering due to enviroment variables not present in building environment
export const dynamic = 'force-dynamic'

const EnergyPage = () => {
  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl">Energy</h1>
      <FileUploadForm />
      <AnalysisCardGrid api="energy" />
    </main>
  )
}
export default EnergyPage
