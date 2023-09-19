import { type HelloApiResponse, type HelloSolarResponse } from './solarAnalysisApi.d'

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
}

export default SolarAnalysisApi