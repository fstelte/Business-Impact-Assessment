
(() => {
    'use strict'

    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        return storedTheme || 'dark' // Default to dark if no theme is stored
    }

    const setTheme = theme => {
        document.documentElement.setAttribute('data-bs-theme', theme)
        console.log('Theme set to:', theme) // Debug log
    }

    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme')
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
        setStoredTheme(newTheme)
        setTheme(newTheme)
        updateThemeIcon(newTheme)
    }

    const updateThemeIcon = (theme) => {
        const sunIcon = document.querySelector('.bi-sun-fill')
        const moonIcon = document.querySelector('.bi-moon-stars-fill')
        
        if (theme === 'dark') {
            sunIcon.style.display = 'none'
            moonIcon.style.display = 'inline-block'
        } else {
            sunIcon.style.display = 'inline-block'
            moonIcon.style.display = 'none'
        }
    }

    // Set initial theme
    const initialTheme = getPreferredTheme()
    setTheme(initialTheme)
    updateThemeIcon(initialTheme)

    // Add event listener to theme switcher
    window.addEventListener('DOMContentLoaded', () => {
        const themeSwitcher = document.getElementById('theme-switcher')
        if (themeSwitcher) {
            console.log('Theme switcher found') // Debug log
            themeSwitcher.addEventListener('click', toggleTheme)
        } else {
            console.error('Theme switcher button not found') // Debug log
        }
    })
})()