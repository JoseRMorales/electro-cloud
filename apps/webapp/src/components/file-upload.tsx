'use client'

import { FileInput, Label } from 'flowbite-react'

interface FileUploadProps {
  required?: boolean
}

const FileUpload = ({ required = false }: FileUploadProps) => {
  return (
    <div
      className="max-w-md"
      id="fileUpload"
    >
      <div className="mb-2 block">
        <Label
          htmlFor="consumption_file"
          value="Upload file"
        />
      </div>
      <FileInput
        helperText="Select file"
        id="consumption_file"
        name="consumption_file"
        required
      />
    </div>
  )
}

export default FileUpload
