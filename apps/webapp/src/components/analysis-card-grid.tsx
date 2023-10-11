import SolarAnalysisApi from '@/api/solarAnalysisApi'

import AnalysisCard from './ui/analysis-card'

const AnalysisCardGrid = async () => {
  const api = new SolarAnalysisApi()
  const { results } = await api.getAllResultsTimeSlots()

  results.sort((a, b) => {
    const aDate = new Date(a.created_at)
    const bDate = new Date(b.created_at)
    return bDate.getTime() - aDate.getTime()
  })

  return (
    <>
      <h2 className='text-2xl'>Recent Analysis</h2>
      <article className='flex flex-wrap gap-4 items-center justify-center'>
        {
          results.map((result) => (
            <AnalysisCard
              key={result.analysisId}
              analysisId={result.analysisId}
              holder={result.holder ?? undefined}
              name={result.name ?? undefined}
              created_at={result.created_at}
            />
          ))
        }
      </article>
    </>
  )
}
export default AnalysisCardGrid
