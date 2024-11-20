'use client'
import { Button } from '@/components/ui/button'

// @ts-ignore
import { useActionState } from 'react'
// @ts-ignore
import { useFormStatus } from 'react-dom'

import { postEnergyFile } from '@/actions/energy-form'

import FileUpload from './file-upload'

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

const FileUploadForm = () => {
  const [state, formAction] = useActionState(postEnergyFile, initialState)

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <FileUpload required />
      <SubmitButton />
      {state?.message && <p>{state.message}</p>}
    </form>
  )
}
export default FileUploadForm
