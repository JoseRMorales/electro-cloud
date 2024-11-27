'use client'
import { postSolarForm } from '@/actions/energy-form'
import FileUpload from '@/components/file-upload'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'

const initialState = {
  message: null
}

const SubmitButton = () => {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" disabled={pending}>
      Submit
    </Button>
  )
}

const SolarForm = () => {
  const [state, formAction] = useActionState(postSolarForm, initialState)

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <FileUpload required />
      <div className="grid w-full max-w-sm items-center gap-1.5 grid-cols-2">
        <Label htmlFor="location">Location</Label>
        <Input id="location" name="location" placeholder="Madrid" required />
        <Label htmlFor="peakpower">Peak Power in kW</Label>
        <Input id="peakpower" name="peakpower" placeholder="5" required />
        <Label htmlFor="mountingplace">Mounting Place</Label>
        <Input
          id="mountingplace"
          name="mountingplace"
          placeholder="building"
          required
        />
        <Label htmlFor="loss">System Loss</Label>
        <Input id="loss" name="loss" placeholder="7" required />
        <Label htmlFor="angle">Angle</Label>
        <Input id="angle" name="angle" placeholder="30" required />
        <Label htmlFor="aspect">Azimuth</Label>
        <Input id="aspect" name="aspect" placeholder="0" required />
      </div>
      <SubmitButton />
      {state?.message && <p>{state.message}</p>}
    </form>
  )
}

export default SolarForm
