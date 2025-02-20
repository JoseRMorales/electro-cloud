'use server'

import { SelfPercentRatiosResponse } from '@/api/responses'
import SolarAnalysisApi from '@/api/solarAnalysisApi'
import AdmZip from 'adm-zip'

export const getSolarConsumptionProductionPlot = async (
  analysisId: string
): Promise<string> => {
  const api = new SolarAnalysisApi()
  const blob = await api.getSolarConsumptionProductionPlot(analysisId)

  const arrayBuffer = await blob.arrayBuffer()
  const base64String = Buffer.from(arrayBuffer).toString('base64')
  return `data:image/png;base64,${base64String}`
}

export const getSolarMonthlyPlots = async (
  analysisId: string
): Promise<string[]> => {
  const api = new SolarAnalysisApi()
  const zipBuffer = await api.getSolarMonthlyPlots(analysisId)

  // Use adm-zip to extract the contents
  const zip = new AdmZip(Buffer.from(zipBuffer))
  const zipEntries = zip.getEntries()

  // Convert each image to Base64
  const images = zipEntries
    .filter(
      (entry) =>
        !entry.isDirectory && /\.(png|jpg|jpeg|gif)$/i.test(entry.entryName)
    ) // Filter for image files
    .map((entry) => {
      const imageBuffer = entry.getData()
      const base64String = `data:image/${entry.entryName.split('.').pop()};base64,${imageBuffer.toString('base64')}`
      return base64String
    })

  return images // Array of Base64-encoded images
}

export const getSolarSelfPercentRatios = async (
  analysisId: string
): Promise<SelfPercentRatiosResponse> => {
  const api = new SolarAnalysisApi()
  const data = await api.getSolarSelfPercentRatios(analysisId)

  return data
}

export const getSolarMonthlyProduction = async (
  analysisId: string
): Promise<string> => {
  const api = new SolarAnalysisApi()
  const data = await api.getSolarMonthlyProduction(analysisId)

  return data
}

export const getSolarMonthlyConsumption = async (
  analysisId: string
): Promise<string> => {
  const api = new SolarAnalysisApi()
  const data = await api.getSolarMonthlyConsumption(analysisId)

  return data
}
