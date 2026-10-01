package com.adel.banshar
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
class BackupReceiver:BroadcastReceiver(){override fun onReceive(c:Context,i:Intent?){when(i?.action){Intent.ACTION_BOOT_COMPLETED,Intent.ACTION_MY_PACKAGE_REPLACED->BackupScheduler.schedule(c);else->if(BackupManager.isEnabled(c))BackupManager.create(c)}}}