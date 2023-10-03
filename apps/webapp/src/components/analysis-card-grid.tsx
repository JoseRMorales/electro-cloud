import SolarAnalysisApi from '@/api/solarAnalysisApi'

import AnalysisCard from './ui/analysis-card'

const AnalysisCardGrid = async () => {
  const api = new SolarAnalysisApi()
  const { results } = await api.getAllResultsTimeSlots()

  return (
    <>
      <h2 className='text-2xl'>Recent Analysis</h2>
      <article className='flex flex-wrap gap-4'>
        {
          results.map((result) => (
            <AnalysisCard
              key={result.analysisId}
              analysisId={result.analysisId}
              holder={result.holder}
              name={result.name}
            />
          ))
        }
      </article>
    </>
  )
}
export default AnalysisCardGrid
