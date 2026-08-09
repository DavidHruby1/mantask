import type { FormErrors } from '@/interfaces'

const PASSWORD_REGEX = /^[A-Za-z0-9_!@#$%^&*()[\]{};<>?/\\|~."+',`=:-]+$/
const NAME_REGEX = /^[a-zA-Z0-9\-_: ]+$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// Validates username and stores its current error in the supplied error object.
export function validateUsername(value: string, errors: FormErrors): boolean {
    const username = value.trim()

    if (username === '') errors.username = 'Username is required'
    else if (/\s/.test(username)) errors.username = 'There can be no whitespace in username'
    else if (username.length < 3) errors.username = 'Username is too short'
    else if (username.length > 50) errors.username = 'Username is too long'
    else errors.username = ''

    return errors.username === ''
}

// Validates email and stores its current error in the supplied error object.
export function validateEmail(value: string, errors: FormErrors): boolean {
    const email = value.trim()

    if (email === '') errors.email = 'Email is required'
    else if (!EMAIL_REGEX.test(email)) errors.email = 'Email is invalid'
    else errors.email = ''

    return errors.email === ''
}

// Validates password and stores its current error in the supplied error object.
export function validatePassword(value: string, errors: FormErrors): boolean {
    if (value.length < 8) errors.password = 'Password is too short'
    else if (value.length > 128) errors.password = 'Password is too long'
    else if (/\s/.test(value)) errors.password = 'There can be no whitespace in password'
    else if (!PASSWORD_REGEX.test(value)) errors.password = 'Password contains invalid characters'
    else errors.password = ''

    return errors.password === ''
}

// Validates an organization or team name and stores its current error.
export function validateOrganizationOrTeamName(
    value: string,
    field: 'organization' | 'team',
    errors: FormErrors
): boolean {
    const name = value.trim()
    const label = field === 'organization' ? 'Organization name' : 'Team name'

    if (name === '') errors[field] = `${label} is required`
    else if (name.length > 100) errors[field] = `${label} is too long`
    else if (!NAME_REGEX.test(name)) errors[field] = `${label} contains invalid characters`
    else errors[field] = ''

    return errors[field] === ''
}

// Validates the bootstrap secret and stores its current error in the error object.
export function validateBootstrapSecret(value: string, errors: FormErrors): boolean {
    if (value.length < 32) errors.bootstrapSecret = 'Bootstrap secret is too short'
    else if (value.length > 256) errors.bootstrapSecret = 'Bootstrap secret is too long'
    else errors.bootstrapSecret = ''

    return errors.bootstrapSecret === ''
}
