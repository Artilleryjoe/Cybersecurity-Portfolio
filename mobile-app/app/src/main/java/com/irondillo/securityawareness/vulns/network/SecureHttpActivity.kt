package com.irondillo.securityawareness.vulns.network

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.net.URL

/**
 * Demonstrates using HTTPS for secure communication.
 */
class SecureHttpActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Thread {
            URL("https://example.com").openConnection().getInputStream().use { }
        }.start()
    }
}

