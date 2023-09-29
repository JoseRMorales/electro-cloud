import { type EnergyProcessFileResponse, type HelloApiResponse, type HelloSolarResponse } from './responses'

class SolarAnalysisApi {
  private readonly url: string

  constructor () {
    this.url = process.env.SOLAR_ANALYSIS_API_URL ?? (() => { throw new Error('SOLAR_ANALYSIS_API_URL is not defined') })()
  }

  async getHelloApi (): Promise<string> {
    const res = await fetch(`${this.url}/`)
    const data = await res.json() as HelloApiResponse
    const { message } = data
    return message
  }

  async getHelloSolar (): Promise<string> {
    const res = await fetch(`${this.url}/solar/`)
    const data = await res.json() as HelloSolarResponse
    const { message } = data
    return message
  }

  async postEnergyFile (formData: FormData): Promise<string> {
    // Extract the file from the FormData object
    const res = await fetch(`${this.url}/energy/process-file`, {
      method: 'POST',
      body: formData
    })
    const data = await res.json() as EnergyProcessFileResponse
    const { analysisId } = data
    return analysisId
  }

  async getEnergyByTimeSlot (analysisId: string): Promise<string> {
    console.log('analysisId', analysisId)
    const res = await fetch(`${this.url}/energy/energy-time-slot/${analysisId}`)
    const data = await res.text()
    return data
  }
}

export default SolarAnalysisApi
