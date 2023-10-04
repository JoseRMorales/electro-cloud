'use server'

import { revalidatePath } from 'next/cache'

import SolarAnalysisApi from '@/api/solarAnalysisApi'
import { type IAction } from '@/types/action-types'

export const postEnergyFile = async (prevState: any, formData: FormData) => {
  const api = new SolarAnalysisApi()
  const analysisId = await api.postEnergyFile(formData)
  console.log('analysisId', analysisId)
  revalidatePath('/energy')
}

export const getEnergyByTimeSlot = async (analysisId: string): Promise<IAction> => {
  const api = new SolarAnalysisApi()
  const data = await api.getEnergyByTimeSlot(analysisId)

  return data
}

export const deleteAnalysis = async (analysisId: string, formData: FormData) => {
  console.log('analysisId', analysisId)
  console.log('formData', formData)
  const api = new SolarAnalysisApi()
  await api.deleteAnalysis(analysisId)

  revalidatePath('/energy')
}
