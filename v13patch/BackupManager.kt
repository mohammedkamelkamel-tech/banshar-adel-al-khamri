package com.adel.banshar
import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
object BackupManager {
 private const val P="backup_settings"; private const val KEEP=7
 const val FOLDER="Download/بنشر عادل الخامري/نسخ احتياطية"
 fun isEnabled(c:Context)=c.getSharedPreferences(P,0).getBoolean("enabled",true)
 fun hour(c:Context)=c.getSharedPreferences(P,0).getInt("hour",2)
 fun minute(c:Context)=c.getSharedPreferences(P,0).getInt("minute",0)
 fun last(c:Context)=c.getSharedPreferences(P,0).getString("last","لم يتم إنشاء نسخة بعد") ?: "لم يتم إنشاء نسخة بعد"
 fun configure(c:Context,e:Boolean,h:Int,m:Int){c.getSharedPreferences(P,0).edit().putBoolean("enabled",e).putInt("hour",h).putInt("minute",m).apply();if(e)BackupScheduler.schedule(c)else BackupScheduler.cancel(c)}
 fun create(c:Context):Boolean{
  val tmp=File(c.cacheDir,"backup-\${System.currentTimeMillis()}.db")
  return try{
   val db=Db(c);val path=tmp.absolutePath.replace("'","''");db.writableDatabase.execSQL("VACUUM INTO '\$path'");db.close()
   if(!tmp.exists()||tmp.length()==0L)return false
   val name="banshar-adel-backup-"+SimpleDateFormat("yyyy-MM-dd_HH-mm-ss",Locale.US).format(Date())+".db"
   val ok=if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q){
    val v=ContentValues().apply{put(MediaStore.MediaColumns.DISPLAY_NAME,name);put(MediaStore.MediaColumns.MIME_TYPE,"application/octet-stream");put(MediaStore.MediaColumns.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/بنشر عادل الخامري/نسخ احتياطية")}
    val u=c.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v)
    if(u==null)false else try{c.contentResolver.openOutputStream(u)?.use{o->tmp.inputStream().use{it.copyTo(o)}};true}catch(_:Exception){c.contentResolver.delete(u,null,null);false}
   }else{val d=File(c.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS),"نسخ احتياطية");d.mkdirs();tmp.copyTo(File(d,name),true);true}
   if(ok){c.getSharedPreferences(P,0).edit().putString("last",SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.US).format(Date())).apply();cleanup(c)};ok
  }catch(_:Exception){false}finally{tmp.delete()}
 }
 fun restore(c:Context,u:Uri):Boolean {
  return try {
   val db=Db(c);db.close();val f=c.getDatabasePath("banshar.db");val t=File(c.cacheDir,"restore.db")
   c.contentResolver.openInputStream(u)?.use{i->t.outputStream().use{o->i.copyTo(o)}} ?: return false
   if(!t.exists()||t.length()==0L)return false
   t.copyTo(f,true);t.delete();File(f.absolutePath+"-wal").delete();File(f.absolutePath+"-shm").delete();true
  } catch(_:Exception){false}
 }
 private fun cleanup(c:Context){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.Q)return;try{
  val u=MediaStore.Downloads.EXTERNAL_CONTENT_URI;val ids=mutableListOf<Long>()
  c.contentResolver.query(u,arrayOf("_id",MediaStore.MediaColumns.DISPLAY_NAME),"\${MediaStore.MediaColumns.RELATIVE_PATH}=?",arrayOf(Environment.DIRECTORY_DOWNLOADS+"/بنشر عادل الخامري/نسخ احتياطية/"),"\${MediaStore.MediaColumns.DATE_MODIFIED} DESC")?.use{x->while(x.moveToNext()){val n=x.getString(1)?:"";if(n.startsWith("banshar-adel-backup-")&&n.endsWith(".db"))ids+=x.getLong(0)}}
  ids.drop(KEEP).forEach{c.contentResolver.delete(u,"_id=?",arrayOf(it.toString()))}
 }catch(_:Exception){}}
}