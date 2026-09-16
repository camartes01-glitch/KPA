import { describe, it, expect } from 'vitest'
import { extractErrorMessage } from '../lib/api'
import axios from 'axios'

describe('Web Admin API Client & Error Normalization', () => {
  it('handles standard Javascript Error instance', () => {
    const error = new Error('Network timeout')
    expect(extractErrorMessage(error)).toBe('Network timeout')
  })

  it('handles network disconnection (no response object)', () => {
    const axiosError = new axios.AxiosError('Network Error')
    expect(extractErrorMessage(axiosError)).toContain('Unable to connect to KPA server')
  })

  it('handles 422 FastAPI validation errors with field locations', () => {
    const axiosError = new axios.AxiosError('Unprocessable Entity')
    axiosError.response = {
      status: 422,
      data: {
        detail: [
          { loc: ['body', 'phone'], msg: 'Invalid phone number format' },
          { loc: ['body', 'amount'], msg: 'Amount must be positive' },
        ],
      },
      statusText: 'Unprocessable Entity',
      headers: {},
      config: {} as any,
    }

    const msg = extractErrorMessage(axiosError)
    expect(msg).toBe('Invalid phone number format, Amount must be positive')
  })

  it('handles custom backend detail messages', () => {
    const axiosError = new axios.AxiosError('Bad Request')
    axiosError.response = {
      status: 400,
      data: { detail: 'Only approved members can receive welfare relief.' },
      statusText: 'Bad Request',
      headers: {},
      config: {} as any,
    }

    expect(extractErrorMessage(axiosError)).toBe('Only approved members can receive welfare relief.')
  })

  it('handles fallback HTTP status code messages', () => {
    const forbiddenError = new axios.AxiosError('Forbidden')
    forbiddenError.response = {
      status: 403,
      data: {},
      statusText: 'Forbidden',
      headers: {},
      config: {} as any,
    }
    expect(extractErrorMessage(forbiddenError)).toBe('You do not have permission to perform this action.')

    const notFoundError = new axios.AxiosError('Not Found')
    notFoundError.response = {
      status: 404,
      data: {},
      statusText: 'Not Found',
      headers: {},
      config: {} as any,
    }
    expect(extractErrorMessage(notFoundError)).toBe('The requested resource was not found.')
  })
})
