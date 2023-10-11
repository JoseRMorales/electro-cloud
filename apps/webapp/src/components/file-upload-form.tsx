/* eslint-disable @typescript-eslint/strict-boolean-expressions */
'use client'
import { Button } from 'flowbite-react'
import { experimental_useFormState as useFormState, experimental_useFormStatus as useFormStatus } from 'react-dom'

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
  const [state, formAction] = useFormState(postEnergyFile, initialState)

  return (
    // @ts-expect-error Experimental Form Action
    <form action={formAction} >
      <FileUpload required/>
      <SubmitButton />
      {state?.message && <p>{state.message}</p>}
    </form>
  )
}
export default FileUploadForm
