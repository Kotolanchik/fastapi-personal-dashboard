import { FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { changePassword, updateProfile } from '../../shared/api/auth'
import { useToast } from '../../shared/components/Toast'
import { downloadCsv, type ExportCategory } from '../../shared/api/export'
import { getErrorMessage, parseValidationErrors } from '../../shared/utils/validation'

const COMMON_TIMEZONES = [
  'UTC',
  'Europe/Moscow',
  'Europe/London',
  'Europe/Berlin',
  'America/New_York',
  'America/Los_Angeles',
  'Asia/Tokyo',
  'Asia/Shanghai',
]

export const SettingsPage = () => {
  const { user, refreshUser } = useAuth()
  const toast = useToast()
  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [defaultTimezone, setDefaultTimezone] = useState(user?.default_timezone ?? 'UTC')
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileErrors, setProfileErrors] = useState<Record<string, string>>({})
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordSaving, setPasswordSaving] = useState(false)
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({})
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    setFullName(user?.full_name ?? '')
    setDefaultTimezone(user?.default_timezone ?? 'UTC')
  }, [user])

  const handleProfileSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setProfileErrors({})
    setProfileSaving(true)
    try {
      await updateProfile({ full_name: fullName || null, default_timezone: defaultTimezone || 'UTC' })
      await refreshUser()
      toast.success('Profile saved.')
    } catch (err) {
      const errors = parseValidationErrors(err)
      setProfileErrors(errors)
      if (Object.keys(errors).length === 0) toast.error(getErrorMessage(err))
    } finally {
      setProfileSaving(false)
    }
  }

  const handlePasswordSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setPasswordErrors({})
    if (newPassword !== confirmPassword) {
      setPasswordErrors({ new_password: 'Passwords do not match', confirm_password: 'Passwords do not match' })
      return
    }
    setPasswordSaving(true)
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword })
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      toast.success('Password changed.')
    } catch (err) {
      const errors = parseValidationErrors(err)
      setPasswordErrors(errors)
      if (Object.keys(errors).length === 0) toast.error(getErrorMessage(err))
    } finally {
      setPasswordSaving(false)
    }
  }

  const handleDownloadCsv = async (category: ExportCategory = 'all') => {
    setExporting(true)
    try {
      await downloadCsv(category)
      toast.success('CSV downloaded.')
    } catch {
      toast.error('Download failed.')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="stack">
      <div className="card">
        <h3>Profile</h3>
        <p className="muted">Update your name and default timezone.</p>
        <form onSubmit={handleProfileSubmit} className="form-grid">
          <label>
            Name
            <input
              type="text"
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value)
                setProfileErrors((p) => ({ ...p, full_name: undefined }))
              }}
              aria-invalid={!!profileErrors.full_name}
            />
            {profileErrors.full_name ? <div className="field-error">{profileErrors.full_name}</div> : null}
          </label>
          <label>
            Default timezone
            <select
              value={defaultTimezone}
              onChange={(e) => {
                setDefaultTimezone(e.target.value)
                setProfileErrors((p) => ({ ...p, default_timezone: undefined }))
              }}
              aria-invalid={!!profileErrors.default_timezone}
            >
              {COMMON_TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz}
                </option>
              ))}
            </select>
            {profileErrors.default_timezone ? (
              <div className="field-error">{profileErrors.default_timezone}</div>
            ) : null}
          </label>
          <div className="form-actions">
            <button type="submit" disabled={profileSaving}>
              {profileSaving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3>Change password</h3>
        <form onSubmit={handlePasswordSubmit} className="form-grid">
          <label>
            Current password
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => {
                setCurrentPassword(e.target.value)
                setPasswordErrors((p) => ({ ...p, current_password: undefined }))
              }}
              required
              aria-invalid={!!passwordErrors.current_password}
            />
            {passwordErrors.current_password ? (
              <div className="field-error">{passwordErrors.current_password}</div>
            ) : null}
          </label>
          <label>
            New password
            <input
              type="password"
              value={newPassword}
              onChange={(e) => {
                setNewPassword(e.target.value)
                setPasswordErrors((p) => ({ ...p, new_password: undefined }))
              }}
              required
              minLength={8}
              aria-invalid={!!passwordErrors.new_password}
            />
            {passwordErrors.new_password ? (
              <div className="field-error">{passwordErrors.new_password}</div>
            ) : null}
          </label>
          <label>
            Confirm new password
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value)
                setPasswordErrors((p) => ({ ...p, confirm_password: undefined }))
              }}
              required
              minLength={8}
              aria-invalid={!!passwordErrors.confirm_password}
            />
            {passwordErrors.confirm_password ? (
              <div className="field-error">{passwordErrors.confirm_password}</div>
            ) : null}
          </label>
          <div className="form-actions">
            <button type="submit" disabled={passwordSaving}>
              {passwordSaving ? 'Saving…' : 'Change password'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3>Export data</h3>
        <p className="muted">Download your entries as CSV.</p>
        <div className="form-actions">
          <button type="button" disabled={exporting} onClick={() => handleDownloadCsv('all')}>
            {exporting ? '…' : 'Download CSV'}
          </button>
        </div>
      </div>
    </div>
  )
}
