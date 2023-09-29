'use client'
import { Button } from 'flowbite-react'
const LoadingButton = () => {
  return (
    <Button
        isProcessing
        size="xs"
      >
      <p>
        Click me!
      </p>
    </Button>
  )
}
export default LoadingButton
