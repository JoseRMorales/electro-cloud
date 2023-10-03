import AnalysisCardGrid from '@/components/analysis-card-grid'
import FileUploadForm from '@/components/file-upload-form'

const EnergyPage = () => {
  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl">Energy</h1>
      <FileUploadForm />
      <AnalysisCardGrid />
    </main>
  )
}
export default EnergyPage
