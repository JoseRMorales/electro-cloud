'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

import SolarAnalysisApi from '@/api/solarAnalysisApi'
import { type IAction } from '@/types/action-types'

export const postEnergyFile = async (prevState: any, formData: FormData) => {
  const api = new SolarAnalysisApi()
  const analysisId = await api.postEnergyFile(formData)
  revalidatePath('/energy')
  redirect(`/energy/${analysisId}`)
}

export const getEnergyByTimeSlot = async (analysisId: string): Promise<IAction> => {
  const api = new SolarAnalysisApi()
  const data = await api.getEnergyByTimeSlot(analysisId)

  return data
}
