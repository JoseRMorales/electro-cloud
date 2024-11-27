'use server'

import { revalidatePath } from 'next/cache'

import SolarAnalysisApi from '@/api/solarAnalysisApi'

export const postEnergyFile = async (prevState: any, formData: FormData) => {
  const api = new SolarAnalysisApi()
  const analysisId = await api.postEnergyFile(formData)
  revalidatePath('/energy')
}

export const getEnergyByTimeSlot = async (
  analysisId: string
): Promise<string> => {
  const api = new SolarAnalysisApi()
  const data = await api.getEnergyByTimeSlot(analysisId)

  return data
}

export const deleteAnalysis = async (
  analysisId: string,
  formData: FormData
) => {
  const api = new SolarAnalysisApi()
  await api.deleteAnalysis(analysisId)

  revalidatePath('/energy')
}

export const postSolarForm = async (prevState: any, formData: FormData) => {
  const api = new SolarAnalysisApi()
  const analysisId = await api.postSolarForm(formData)
  revalidatePath('/solar')
}
