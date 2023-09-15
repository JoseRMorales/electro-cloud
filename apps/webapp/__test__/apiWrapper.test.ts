import { describe, expect, it } from 'vitest'
import SolarAnalysisApi from '../src/lib/solarAnalysisApi'

describe('SolarAnalysisApi wrapper', () => {
  const api = new SolarAnalysisApi()

  it('should return "Hello Api!" the method "getHelloWorld"', async () => {
    const res = await api.getHelloApi()
    expect(res).toBe('Hello Api!')
  })
})
