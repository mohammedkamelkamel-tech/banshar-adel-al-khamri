from pathlib import Path

root=Path('.')
(root/'app/src/main/java/com/adel/banshar/AutoBackup.kt').write_text(r'''package com.adel.banshar

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object AutoBackup {
    private const val PREFS = "auto_backup"
    private const val KEY_LAST = "last_backup"
    private const val KEEP = 7

    fun backup(context: Context): Boolean {
        val temp = File(context.cacheDir, "banshar-auto-${System.currentTimeMillis()}.db")
        return try {
            val db = Db(context)
            val escaped = temp.absolutePath.replace("'", "''")
            db.writableDatabase.execSQL("VACUUM INTO '$escaped'")
            db.close()
            if (!temp.exists() || temp.length() == 0L) return false
            val stamp = SimpleDateFormat("yyyy-MM-dd_HH-mm", Locale.US).format(Date())
            val name = "banshar-adel-backup-$stamp.db"
            val ok = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val values = ContentValues().apply {
                    put(MediaStore.Downloads.DISPLAY_NAME, name)
                    put(MediaStore.Downloads.MIME_TYPE, "application/octet-stream")
                    put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/بنشر عادل الخامري/نسخ احتياطية")
                }
                val uri = context.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                if (uri == null) false else try {
                    context.contentResolver.openOutputStream(uri)?.use { out -> temp.inputStream().use { it.copyTo(out) } }
                    true
                } catch (_: Exception) {
                    context.contentResolver.delete(uri, null, null)
                    false
                }
            } else {
                val dir = File(context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), "نسخ احتياطية")
                if (!dir.exists()) dir.mkdirs()
                temp.copyTo(File(dir, name), overwrite = true)
                true
            }
            if (ok) {
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                    .putString(KEY_LAST, SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US).format(Date()))
                    .apply()
                cleanup(context)
            }
            ok
        } catch (_: Exception) {
            false
        } finally {
            temp.delete()
        }
    }

    fun lastBackup(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_LAST, "لم يتم بعد") ?: "لم يتم بعد"

    private fun cleanup(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return
        try {
            val resolver = context.contentResolver
            val uri = MediaStore.Downloads.EXTERNAL_CONTENT_URI
            val projection = arrayOf(MediaStore.Downloads._ID, MediaStore.Downloads.DISPLAY_NAME)
            val items = mutableListOf<Long>()
            resolver.query(uri, projection, "${MediaStore.Downloads.RELATIVE_PATH}=?", arrayOf(Environment.DIRECTORY_DOWNLOADS + "/بنشر عادل الخامري/نسخ احتياطية/"), "${MediaStore.Downloads.DATE_MODIFIED} DESC")?.use { c ->
                val idCol = c.getColumnIndexOrThrow(MediaStore.Downloads._ID)
                val nameCol = c.getColumnIndexOrThrow(MediaStore.Downloads.DISPLAY_NAME)
                while (c.moveToNext()) {
                    val n = c.getString(nameCol) ?: continue
                    if (n.startsWith("banshar-adel-backup-") && n.endsWith(".db")) items += c.getLong(idCol)
                }
            }
            items.drop(KEEP).forEach { id -> resolver.delete(uri, "${MediaStore.Downloads._ID}=?", arrayOf(id.toString())) }
        } catch (_: Exception) { }
    }
}
''',encoding='utf-8')

(root/'app/src/main/java/com/adel/banshar/AutoBackupReceiver.kt').write_text(r'''package com.adel.banshar

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class AutoBackupReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED -> AutoBackupScheduler.schedule(context)
            else -> AutoBackup.backup(context)
        }
    }
}
''',encoding='utf-8')

(root/'app/src/main/java/com/adel/banshar/AutoBackupScheduler.kt').write_text(r'''package com.adel.banshar

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import java.util.Calendar

object AutoBackupScheduler {
    private const val REQUEST = 9103
    fun schedule(context: Context) {
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(context, AutoBackupReceiver::class.java)
        val pi = PendingIntent.getBroadcast(context, REQUEST, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val now = Calendar.getInstance()
        val first = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 2); set(Calendar.MINUTE, 0); set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
            if (!after(now)) add(Calendar.DAY_OF_YEAR, 1)
        }
        alarm.cancel(pi)
        alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, first.timeInMillis, AlarmManager.INTERVAL_DAY, pi)
    }
}
''',encoding='utf-8')

p=root/'app/src/main/AndroidManifest.xml'; s=p.read_text(encoding='utf-8')
s=s.replace('<uses-permission android:name="android.permission.CAMERA" />','<uses-permission android:name="android.permission.CAMERA" />\n    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />')
s=s.replace('android:theme="@style/Theme.Banshar">','android:theme="@style/Theme.Banshar"\n        android:icon="@drawable/app_icon"\n        android:roundIcon="@drawable/app_icon">')
s=s.replace('        <activity android:name=".CustomerActivity" />','        <receiver android:name=".AutoBackupReceiver" android:exported="false">\n            <intent-filter>\n                <action android:name="android.intent.action.BOOT_COMPLETED" />\n                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />\n            </intent-filter>\n        </receiver>\n        <activity android:name=".CustomerActivity" />')
p.write_text(s,encoding='utf-8')

p=root/'app/src/main/java/com/adel/banshar/MainActivity.kt'; s=p.read_text(encoding='utf-8')
s=s.replace('override fun onCreate(b:Bundle?){super.onCreate(b);setContentView(R.layout.activity_main);','override fun onCreate(b:Bundle?){super.onCreate(b);AutoBackupScheduler.schedule(this);setContentView(R.layout.activity_main);')
s=s.replace('val items=arrayOf("تفعيل / تغيير الرقم السري","نسخ احتياطي لقاعدة البيانات","استرجاع نسخة احتياطية","إغلاق")','val items=arrayOf("تفعيل / تغيير الرقم السري","نسخ احتياطي لقاعدة البيانات","استرجاع نسخة احتياطية","آخر نسخة تلقائية: ${AutoBackup.lastBackup(this)}","إغلاق")')
p.write_text(s,encoding='utf-8')

p=root/'app/build.gradle.kts'; s=p.read_text(encoding='utf-8').replace('versionCode = 11','versionCode = 12').replace('versionName = "1.1.0"','versionName = "1.2.0"'); p.write_text(s,encoding='utf-8')

import base64
Path('app/src/main/res/drawable').mkdir(parents=True,exist_ok=True)
Path('app/src/main/res/drawable/app_icon.png').write_bytes(base64.b64decode(Path('v12patch/icon.b64').read_text()))
