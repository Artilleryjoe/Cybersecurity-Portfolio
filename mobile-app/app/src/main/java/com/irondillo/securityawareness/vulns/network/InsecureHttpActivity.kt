package com.irondillo.securityawareness.vulns.network

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import java.net.URL

class InsecureHttpActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val url = URL("http://example.com")
        url.openConnection().getInputStream()
    }
}
