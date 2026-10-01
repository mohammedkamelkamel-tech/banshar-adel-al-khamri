from pathlib import Path
root=Path(".")

# Keep the selected vehicle wording in reminder messages.
p=root/"app/src/main/java/com/adel/banshar/CustomerActivity.kt"
s=p.read_text(encoding="utf-8")

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
if old not in s:
    raise SystemExit("CustomerActivity message block not found")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")

# Bump version for this message-only update.
p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
s=s.replace('versionCode = 14','versionCode = 15').replace('versionName = "1.4.0"','versionName = "1.5.0"')
p.write_text(s,encoding="utf-8")
