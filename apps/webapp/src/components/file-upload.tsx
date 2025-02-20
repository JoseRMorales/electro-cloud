'use client'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface FileUploadProps {
  required?: boolean
}

const FileUpload = ({ required = false }: FileUploadProps) => {
  return (
    <div className="grid w-full max-w-sm items-center gap-1.5">
      <Label htmlFor="consumption_file">Upload file</Label>
      <Input
        id="consumption_file"
        name="consumption_file"
        required={required}
        type="file"
        placeholder="Upload file"
      />
    </div>
  )
}

export default FileUpload
