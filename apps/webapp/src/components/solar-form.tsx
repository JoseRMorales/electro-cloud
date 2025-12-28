'use client'
import { Plus, Trash2 } from 'lucide-react'
import { useActionState, useState } from 'react'
import { useFormStatus } from 'react-dom'
import { postSolarForm } from '@/actions/energy-form'
import FileUpload from '@/components/file-upload'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const initialState = {
  message: null,
}

const SubmitButton = () => {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" disabled={pending} className="w-full">
      Submit Analysis
    </Button>
  )
}

interface Roof {
  peakpower: string
  mountingplace: string
  loss: string
  angle: string
  aspect: string
}

const SolarForm = () => {
  const [state, formAction] = useActionState(postSolarForm, initialState)
  const [roofs, setRoofs] = useState<Roof[]>([
    {
      peakpower: '5',
      mountingplace: 'building',
      loss: '7',
      angle: '30',
      aspect: '0',
    },
  ])

  const addRoof = () => {
    setRoofs([
      ...roofs,
      {
        peakpower: '5',
        mountingplace: 'building',
        loss: '7',
        angle: '30',
        aspect: '0',
      },
    ])
  }

  const removeRoof = (index: number) => {
    if (roofs.length > 1) {
      setRoofs(roofs.filter((_, i) => i !== index))
    }
  }

  const updateRoof = (index: number, field: keyof Roof, value: string) => {
    const newRoofs = [...roofs]
    newRoofs[index] = { ...newRoofs[index], [field]: value }
    setRoofs(newRoofs)
  }

  return (
    <form action={formAction} className="flex flex-col gap-6 w-full max-w-2xl">
      <div className="bg-card p-6 rounded-lg border shadow-sm">
        <Label htmlFor="location" className="text-lg font-semibold mb-2 block">
          Installation Location
        </Label>
        <Input
          id="location"
          name="location"
          placeholder="e.g. Madrid, Spain"
          required
          className="mb-4"
        />

        <FileUpload />
        <p className="text-sm text-muted-foreground mt-1">
          Optional: Upload a consumption file for self-consumption analysis.
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">Roofs Configuration</h2>
          <Button type="button" variant="outline" size="sm" onClick={addRoof}>
            <Plus className="w-4 h-4 mr-2" />
            Add Roof
          </Button>
        </div>

        {roofs.map((roof, index) => (
          <div
            key={index}
            className="bg-card p-6 rounded-lg border shadow-sm relative"
          >
            {roofs.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 text-destructive"
                onClick={() => removeRoof(index)}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
            <h3 className="text-md font-medium mb-4">Roof #{index + 1}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label>Peak Power (kW)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={roof.peakpower}
                  onChange={(e) =>
                    updateRoof(index, 'peakpower', e.target.value)
                  }
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label>Mounting Place</Label>
                <Input
                  value={roof.mountingplace}
                  onChange={(e) =>
                    updateRoof(index, 'mountingplace', e.target.value)
                  }
                  placeholder="building or free"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label>System Loss (%)</Label>
                <Input
                  type="number"
                  value={roof.loss}
                  onChange={(e) => updateRoof(index, 'loss', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label>Angle (deg)</Label>
                <Input
                  type="number"
                  value={roof.angle}
                  onChange={(e) => updateRoof(index, 'angle', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label>Azimuth (deg)</Label>
                <Input
                  type="number"
                  value={roof.aspect}
                  onChange={(e) => updateRoof(index, 'aspect', e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <input type="hidden" name="roofs" value={JSON.stringify(roofs)} />

      <SubmitButton />
      {state?.message && (
        <p className="text-center p-2 rounded bg-muted">{state.message}</p>
      )}
    </form>
  )
}

export default SolarForm
