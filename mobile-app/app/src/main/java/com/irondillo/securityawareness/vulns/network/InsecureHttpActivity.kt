package com.irondillo.securityawareness.vulns.network

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.net.URL

/**
 * Demonstrates an insecure clear-text HTTP call.
 */
class InsecureHttpActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Thread {
            URL("http://example.com").openConnection().getInputStream().use { }
        }.start()
    }
}

