from pathlib import Path
root=Path(".")

p=root/"app/src/main/res/layout/activity_main.xml"
s=p.read_text(encoding="utf-8")
if 'android:id="@+id/btnSettings"' not in s:
    s=s.replace('<EditText android:id="@+id/search"', '<Button android:id="@+id/btnSettings" android:layout_width="match_parent" android:layout_height="wrap_content" android:text="⚙️ الإعدادات"/>\n<EditText android:id="@+id/search"',1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/res/layout/activity_customer.xml"
s=p.read_text(encoding="utf-8")
s=s.replace('<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="نوع الخدمة" android:textStyle="bold" android:paddingTop="8dp"/>\n<Spinner android:id="@+id/serviceType" android:layout_width="match_parent" android:layout_height="wrap_content"/>\n','')
s=s.replace('<TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="نوع الخدمة" android:paddingTop="12dp" />\n<Spinner android:id="@+id/serviceType" android:layout_width="match_parent" android:layout_height="wrap_content" />\n','')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/CustomerActivity.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('; private lateinit var oilType: EditText; private lateinit var serviceType: Spinner','; private lateinit var oilType: EditText')
s=s.replace('    private val serviceOptions = arrayOf("تغيير زيت", "سرويس", "تغيير زيت وسرويس", "فحص وصيانة", "إصلاح بنشر", "خدمة أخرى")\n','')
s=s.replace('serviceType=findViewById(R.id.serviceType); serviceType.adapter=ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, serviceOptions); ','')
s=s.replace('type=findViewById(R.id.serviceType); ','')
s=s.replace(',serviceType=serviceType.selectedItem?.toString().orEmpty()','')
s=s.replace('serviceType.setSelection(serviceOptions.indexOf(c.serviceType).coerceAtLeast(0));','')
old='''    private fun sendSms() {
        val number=phone.text.toString().trim(); if(number.isEmpty()) return
        val msg="عميلنا العزيز ${name.text}: إجمالي الخدمة ${money(existing?.total() ?: 0.0)} ريال، المتبقي ${money(existing?.remaining ?: 0.0)} ريال."
        startActivity(Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:$number")).putExtra("sms_body",msg))
    }
    private fun whatsapp() {
        val number=phone.text.toString().replace("+","").replace(" ",""); if(number.isEmpty()) return
        val msg=Uri.encode("مرحباً ${name.text}، إجمالي الخدمة ${money(existing?.total() ?: 0.0)} ريال، المتبقي ${money(existing?.remaining ?: 0.0)} ريال.")
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/$number?text=$msg"))) } catch (_: Exception) { Toast.makeText(this,"واتساب غير مثبت",Toast.LENGTH_SHORT).show() }
    }
'''
new='''    private fun isMotorcycle(): Boolean {
        val v = vehicle.text.toString().trim()
        return v.contains("دراجة") || v.contains("دباب") || v.contains("نارية") || v.contains("موتور") || v.contains("موتوسيكل")
    }

    private fun oilReminderMessage(): String {
        return if (isMotorcycle()) {
            "حان موعد تغيير زيت الدراجة النارية 🛢️🏍️\\nحياكم الله في بنشر عادل الخامري – فروة، ونتشرف بزيارتكم 🌷"
        } else {
            "حان موعد تغيير زيت سيارتكم 🛢️🚗\\nحياكم الله في بنشر عادل الخامري – فروة، ونشرف بزيارتكم 🌷"
        }
    }

    private fun sendSms() {
        val number=phone.text.toString().trim(); if(number.isEmpty()) return
        val msg=oilReminderMessage()
        startActivity(Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:$number")).putExtra("sms_body",msg))
    }
    private fun whatsapp() {
        val number=phone.text.toString().replace("+","").replace(" ",""); if(number.isEmpty()) return
        val msg=Uri.encode(oilReminderMessage())
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://wa.me/$number?text=$msg"))) } catch (_: Exception) { Toast.makeText(this,"واتساب غير مثبت",Toast.LENGTH_SHORT).show() }
    }
'''
if old in s:
    s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/Db.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('SQLiteOpenHelper(context, "banshar.db", null, 6)', 'SQLiteOpenHelper(context, "banshar.db", null, 7)')
s=s.replace('    private fun createInventoryTables(db: SQLiteDatabase) {', '''    private fun ensureColumn(db: SQLiteDatabase, table: String, column: String, definition: String) {
        db.rawQuery("PRAGMA table_info($table)", null).use { c ->
            while (c.moveToNext()) if (c.getString(1) == column) return
        }
        db.execSQL("ALTER TABLE $table ADD COLUMN $column $definition")
    }

    private fun repairSchema(db: SQLiteDatabase) {
        ensureColumn(db, "customers", "oilImagePath", "TEXT DEFAULT ''")
        ensureColumn(db, "customers", "serviceType", "TEXT DEFAULT ''")
        ensureColumn(db, "customers", "oilPrice", "REAL DEFAULT 0")
        ensureColumn(db, "customers", "servicePrice", "REAL DEFAULT 0")
        ensureColumn(db, "customers", "paid", "REAL DEFAULT 0")
        ensureColumn(db, "customers", "remaining", "REAL DEFAULT 0")
        ensureColumn(db, "customers", "days", "INTEGER DEFAULT 30")
        ensureColumn(db, "customers", "lastDate", "TEXT")
        ensureColumn(db, "customers", "nextDate", "TEXT")
        ensureColumn(db, "products", "barcode", "TEXT DEFAULT ''")
        ensureColumn(db, "products", "imagePath", "TEXT DEFAULT ''")
        ensureColumn(db, "sales", "customerId", "INTEGER DEFAULT 0")
        ensureColumn(db, "sales", "paid", "REAL DEFAULT 0")
        ensureColumn(db, "sales", "remaining", "REAL DEFAULT 0")
        createInventoryTables(db)
    }

    private fun createInventoryTables(db: SQLiteDatabase) {''')
s=s.replace('        if (oldVersion < 6) createFinanceTables(db)\n', '        if (oldVersion < 6) createFinanceTables(db)\n        if (oldVersion < 7) repairSchema(db)\n')
p.write_text(s,encoding="utf-8")

p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8").replace('versionCode = 14','versionCode = 15').replace('versionName = "1.4.0"','versionName = "1.5.0"')
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/adel/banshar/MainActivity.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('        db = Db(this)\n        list = findViewById', '''        try {
            db = Db(this)
        } catch (e: Exception) {
            Toast.makeText(this, "تعذر فتح قاعدة البيانات. أعد تثبيت النسخة الجديدة.", Toast.LENGTH_LONG).show()
            return
        }
        list = findViewById''')
p.write_text(s,encoding="utf-8")
