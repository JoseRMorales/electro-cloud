/* eslint-disable @typescript-eslint/strict-boolean-expressions */
'use client'
import { Button } from 'flowbite-react'

import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'

import { postEnergyFile } from '@/actions/energy-form'

import FileUpload from './file-upload'

const initialState = {
  message: null
}

const SubmitButton = () => {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" isProcessing={pending} size="xs">
      Submit
    </Button>
  )
}

const FileUploadForm = () => {
  const [state, formAction] = useActionState(postEnergyFile, initialState)

  return (
    <form action={formAction}>
      <FileUpload required />
      <SubmitButton />
      {state?.message && <p>{state.message}</p>}
    </form>
  )
}
export default FileUploadForm
