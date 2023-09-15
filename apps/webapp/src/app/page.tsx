import { Button } from '@/components/ui/button'
import { ModeToggle } from '@/components/ui/mode-toggle'
import SolarAnalysisApi from '@/lib/solarAnalysisApi'

export default function Home () {
  const api = new SolarAnalysisApi()

  return (
    <main>
      <h1>Hello World!</h1>
      <Button>Click me</Button>
      <ModeToggle />
      {
        api.getHelloApi()
          .then((res) => <p>{res}</p>)
      }
    </main>
  )
}
