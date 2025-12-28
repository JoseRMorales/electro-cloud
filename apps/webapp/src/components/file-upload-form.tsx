'use client'

import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'
import { postEnergyFile } from '@/actions/energy-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import FileUpload from './file-upload'

const initialState: { message: string | null } = {
  message: null,
}

const SubmitButton = () => {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" disabled={pending}>
      Submit
    </Button>
  )
}

const FileUploadForm = () => {
  const [state, formAction] = useActionState(postEnergyFile, initialState)

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <div className="grid w-full max-w-sm items-center gap-1.5">
        <Label htmlFor="name">Analysis Name (Optional)</Label>
        <Input id="name" name="name" placeholder="My Energy Analysis" />
      </div>
      <FileUpload required />
      <SubmitButton />
      {state?.message && <p>{state.message}</p>}
    </form>
  )
}
export default FileUploadForm
