import SolarAnalysisApi from '@/api/solarAnalysisApi'

import AnalysisCard from './ui/analysis-card'

const AnalysisCardGrid = async () => {
  const api = new SolarAnalysisApi()
  const { results } = await api.getAllResultsTimeSlots()

  const resultsWithDate = results.map((result) => {
    const epoch = Number(result.created_at) * 1000

    const date = new Date(epoch).toLocaleString()
    return {
      analysisId: result.analysisId,
      created_at: date
    }
  })

  resultsWithDate.sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  return (
    <>
      <h2 className="text-2xl">Recent Analysis</h2>
      <article className="flex flex-wrap gap-4 items-center justify-center">
        {resultsWithDate.map((result) => (
          <AnalysisCard
            key={result.analysisId}
            analysisId={result.analysisId}
            created_at={result.created_at}
          />
        ))}
      </article>
    </>
  )
}
export default AnalysisCardGrid
