import AnalysisCardGrid from '@/components/analysis-card-grid'
import FileUploadForm from '@/components/file-upload-form'

const SolarPage = () => {
  return (
    <main className="flex flex-col items-center justify-center p-6 gap-4">
      <h1 className="text-5xl">Solar</h1>
      <FileUploadForm />
      <AnalysisCardGrid api="solar" />
    </main>
  )
}
export default SolarPage
