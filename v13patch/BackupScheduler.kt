package com.adel.banshar
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import java.util.Calendar
object BackupScheduler{
 private const val R=9130
 fun schedule(c:Context){if(!BackupManager.isEnabled(c))return;val a=c.getSystemService(Context.ALARM_SERVICE) as AlarmManager;val p=PendingIntent.getBroadcast(c,R,Intent(c,BackupReceiver::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);val n=Calendar.getInstance();val f=Calendar.getInstance().apply{set(Calendar.HOUR_OF_DAY,BackupManager.hour(c));set(Calendar.MINUTE,BackupManager.minute(c));set(Calendar.SECOND,0);set(Calendar.MILLISECOND,0);if(!after(n))add(Calendar.DAY_OF_YEAR,1)};a.cancel(p);a.setInexactRepeating(AlarmManager.RTC_WAKEUP,f.timeInMillis,AlarmManager.INTERVAL_DAY,p)}
 fun cancel(c:Context){val a=c.getSystemService(Context.ALARM_SERVICE) as AlarmManager;val p=PendingIntent.getBroadcast(c,R,Intent(c,BackupReceiver::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);a.cancel(p)}
}