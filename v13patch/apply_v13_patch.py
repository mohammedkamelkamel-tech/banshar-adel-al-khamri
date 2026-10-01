from pathlib import Path
root=Path(".")

p=root/"app/src/main/res/layout/activity_main.xml"
s=p.read_text(encoding="utf-8").replace('<EditText android:id="@+id/search"', '<Button android:id="@+id/btnSettings" android:layout_width="match_parent" android:layout_height="wrap_content" android:text="⚙️ الإعدادات"/>\n<EditText android:id="@+id/search"')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/res/layout/activity_customer.xml"
s=p.read_text(encoding="utf-8").replace('<EditText android:id="@+id/oilType"', '<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="نوع الخدمة" android:textStyle="bold" android:paddingTop="8dp"/>\n<Spinner android:id="@+id/serviceType" android:layout_width="match_parent" android:layout_height="wrap_content"/>\n<EditText android:id="@+id/oilType"')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/Db.kt"
p.write_text(p.read_text(encoding="utf-8").replace('put("serviceType", "");','put("serviceType", c.serviceType);'),encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/CustomerActivity.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('private lateinit var name: EditText; private lateinit var phone: EditText; private lateinit var vehicle: EditText; private lateinit var oilType: EditText',
'''private lateinit var name: EditText; private lateinit var phone: EditText; private lateinit var vehicle: EditText; private lateinit var oilType: EditText; private lateinit var serviceType: Spinner
    private val serviceOptions = arrayOf("تغيير زيت", "سرويس", "تغيير زيت وسرويس", "فحص وصيانة", "إصلاح بنشر", "خدمة أخرى")''')
s=s.replace('oilType=findViewById(R.id.oilType); days=', 'oilType=findViewById(R.id.oilType); serviceType=findViewById(R.id.serviceType); serviceType.adapter=ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, serviceOptions); days=')
s=s.replace('oilType=oilType.text.toString().trim(),oilImagePath=', 'oilType=oilType.text.toString().trim(),serviceType=serviceType.selectedItem?.toString().orEmpty(),oilImagePath=')
s=s.replace('vehicle.setText(c.vehicle);oilType.setText(c.oilType);days', 'vehicle.setText(c.vehicle);serviceType.setSelection(serviceOptions.indexOf(c.serviceType).coerceAtLeast(0));oilType.setText(c.oilType);days')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/MainActivity.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('import android.os.Bundle','import android.os.Bundle\nimport android.app.TimePickerDialog\nimport android.content.DialogInterface')
s=s.replace('findViewById<Button>(R.id.btnInventory).setOnClickListener { startActivity(Intent(this, InventoryActivity::class.java)) }','findViewById<Button>(R.id.btnInventory).setOnClickListener { startActivity(Intent(this, InventoryActivity::class.java)) }\n        findViewById<Button>(R.id.btnSettings).setOnClickListener { backupSettings() }\n        BackupScheduler.schedule(this)')
block='''    private fun backupSettings() {
        val box=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(28,8,28,8)}
        val auto=CheckBox(this).apply{text="تفعيل النسخ الاحتياطي التلقائي يوميًا";isChecked=BackupManager.isEnabled(this@MainActivity)}
        val time=Button(this).apply{text=String.format(Locale.US,"وقت النسخ: %02d:%02d",BackupManager.hour(this@MainActivity),BackupManager.minute(this@MainActivity))}
        val now=Button(this).apply{text="💾 إنشاء نسخة احتياطية الآن"}
        val restore=Button(this).apply{text="📂 استرجاع نسخة احتياطية"}
        val info=TextView(this).apply{text="مكان الحفظ:\\n"+BackupManager.FOLDER+"\\n\\nآخر نسخة: "+BackupManager.last(this@MainActivity)+"\\nيتم الاحتفاظ بآخر 7 نسخ.";setPadding(0,12,0,12)}
        box.addView(auto);box.addView(time);box.addView(now);box.addView(restore);box.addView(info)
        val d=androidx.appcompat.app.AlertDialog.Builder(this).setTitle("إعدادات النسخ الاحتياطي").setView(box).setPositiveButton("حفظ الإعدادات",null).setNegativeButton("إغلاق",null).create()
        time.setOnClickListener{TimePickerDialog(this,{_,h,m->time.text=String.format(Locale.US,"وقت النسخ: %02d:%02d",h,m);time.tag=h.toString()+":"+m.toString()},BackupManager.hour(this),BackupManager.minute(this),true).show()}
        now.setOnClickListener{val ok=BackupManager.create(this);Toast.makeText(this,if(ok)"تم إنشاء النسخة الاحتياطية بنجاح" else "تعذر إنشاء النسخة الاحتياطية",Toast.LENGTH_LONG).show();info.text="مكان الحفظ:\\n"+BackupManager.FOLDER+"\\n\\nآخر نسخة: "+BackupManager.last(this)+"\\nيتم الاحتفاظ بآخر 7 نسخ."}
        restore.setOnClickListener{startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT).apply{type="application/octet-stream";addCategory(Intent.CATEGORY_OPENABLE)},REQUEST_RESTORE)}
        d.setOnShowListener{d.getButton(DialogInterface.BUTTON_POSITIVE).setOnClickListener{val q=(time.tag?.toString() ?: BackupManager.hour(this).toString()+":"+BackupManager.minute(this).toString()).split(":");val h=q.getOrNull(0)?.toIntOrNull()?:2;val m=q.getOrNull(1)?.toIntOrNull()?:0;BackupManager.configure(this,auto.isChecked,h.coerceIn(0,23),m.coerceIn(0,59));Toast.makeText(this,if(auto.isChecked)"تم حفظ إعدادات النسخ وسيتم النسخ يوميًا" else "تم إيقاف النسخ التلقائي",Toast.LENGTH_SHORT).show();d.dismiss()}}
        d.show()
    }
    override fun onActivityResult(r:Int,result:Int,data:Intent?){super.onActivityResult(r,result,data);if(r==REQUEST_RESTORE&&result==RESULT_OK&&data?.data!=null){val ok=BackupManager.restore(this,data.data!!);if(ok){db=Db(this);showList(db.all());Toast.makeText(this,"تم استرجاع النسخة. يفضّل إعادة فتح التطبيق.",Toast.LENGTH_LONG).show()}else Toast.makeText(this,"تعذر استرجاع النسخة الاحتياطية",Toast.LENGTH_LONG).show()}}
'''
s=s.replace('    private fun showList(items: List<Customer>) {',block+'\n    private fun showList(items: List<Customer>) {')
s=s.replace('    private var showingDue = false','    private var showingDue = false\n    companion object { const val REQUEST_RESTORE = 9131 }')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/AndroidManifest.xml"
s=p.read_text(encoding="utf-8").replace('<receiver android:name=".ReminderReceiver" android:exported="false" />','<receiver android:name=".ReminderReceiver" android:exported="false" />\n        <receiver android:name=".BackupReceiver" android:exported="false"><intent-filter><action android:name="android.intent.action.BOOT_COMPLETED"/><action android:name="android.intent.action.MY_PACKAGE_REPLACED"/></intent-filter></receiver>')
p.write_text(s,encoding="utf-8")

p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8").replace('versionCode = 1','versionCode = 13').replace('versionName = "1.0"','versionName = "1.3.0"')
p.write_text(s,encoding="utf-8")


# Final idempotent fixes
p=root/"app/src/main/res/layout/activity_main.xml"
s=p.read_text(encoding="utf-8")
if 'android:id="@+id/btnSettings"' not in s:
    s=s.replace('<EditText android:id="@+id/search"', '<Button android:id="@+id/btnSettings" android:layout_width="match_parent" android:layout_height="wrap_content" android:text="⚙️ الإعدادات"/>\n<EditText android:id="@+id/search"', 1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/MainActivity.kt"
s=p.read_text(encoding="utf-8")
if 'REQUEST_RESTORE' not in s:
    s=s.replace('    private fun showList(items: List<Customer>) {','    companion object { const val REQUEST_RESTORE = 9131 }\n\n    private fun showList(items: List<Customer>) {',1)
p.write_text(s,encoding="utf-8")


# Make settings button independent of XML resource generation
p=root/"app/src/main/java/com/adel/banshar/MainActivity.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('findViewById<Button>(R.id.btnSettings).setOnClickListener { backupSettings() }',
'''val rootLayout=findViewById<LinearLayout>(android.R.id.content).getChildAt(0) as LinearLayout
        val settingsButton=Button(this).apply{text="⚙️ الإعدادات";setOnClickListener{backupSettings()}}
        rootLayout.addView(settingsButton,2)''')
if 'companion object { const val REQUEST_RESTORE' not in s:
    s=s.replace('    private fun showList(items: List<Customer>) {','    companion object { const val REQUEST_RESTORE = 9131 }\n\n    private fun showList(items: List<Customer>) {',1)
p.write_text(s,encoding="utf-8")
