// ═════════════════════════════════════════════════════════════════════════════
// 🚀 GlobleXGPT Pro Plan Management System - Enhanced Google Apps Script
// ═════════════════════════════════════════════════════════════════════════════
// 
// FEATURES:
// ✅ Complete Razorpay payment tracking with transaction IDs
// ✅ Promo code usage monitoring
// ✅ User registration tracking
// ✅ Payment method details (Card, UPI, Wallet, NetBanking)
// ✅ Automatic 30-day validity calculation
// ✅ Real-time status updates
// ✅ Comprehensive audit trail
// ✅ IP address logging for security
// ✅ Failed payment tracking
// 
// DEPLOYMENT INSTRUCTIONS:
// 1. Go to https://script.google.com/home
// 2. Create a new project or open your existing Google Sheet
// 3. Go to Extensions > Apps Script
// 4. Paste this entire code into Code.gs
// 5. Save the project (Ctrl+S)
// 6. Click "Deploy" > "New deployment"
// 7. Select type: "Web app"
// 8. Set Description: "GlobleXGPT Pro Plan Manager v3.0"
// 9. Set execute as: "Me (your email)"
// 10. Set who has access: "Anyone" (CRITICAL!)
// 11. Click "Deploy" and copy the "Web app URL"
// 12. Paste URL into your .env file as GOOGLE_SHEETS_SCRIPT_URL
// 13. Run setupSheets() function once manually to create all sheets
// ═════════════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────────────
// 📋 SHEET SETUP FUNCTION - Run this once manually
// ─────────────────────────────────────────────────────────────────────────────
function setupSheets() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();

    // Sheet 1: Pro Users (Main tracking)
    var proSheet = ss.getSheetByName("Pro Users") || ss.insertSheet("Pro Users");
    if (proSheet.getLastRow() === 0) {
        proSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Phone",
            "Payment Method",
            "Payment Details",
            "Amount (₹)",
            "Transaction ID",
            "Razorpay Order ID",
            "Razorpay Payment ID",
            "Promo Code",
            "Plan Type",
            "Activation Date",
            "Expiry Date",
            "Days Remaining",
            "Status",
            "IP Address",
            "User Agent"
        ]);
        proSheet.getRange(1, 1, 1, 18).setFontWeight("bold").setBackground("#4285f4").setFontColor("#ffffff");
        proSheet.setFrozenRows(1);
        proSheet.setFrozenColumns(2);
        proSheet.autoResizeColumns(1, 18);
    }

    // Sheet 2: All User Registrations
    var userSheet = ss.getSheetByName("User Registrations") || ss.insertSheet("User Registrations");
    if (userSheet.getLastRow() === 0) {
        userSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Registration Method",
            "Plan Type",
            "IP Address",
            "User Agent"
        ]);
        userSheet.getRange(1, 1, 1, 7).setFontWeight("bold").setBackground("#9c27b0").setFontColor("#ffffff");
        userSheet.setFrozenRows(1);
        userSheet.autoResizeColumns(1, 7);
    }

    // Sheet 3: Promo Code Usage History
    var promoSheet = ss.getSheetByName("Promo Code History") || ss.insertSheet("Promo Code History");
    if (promoSheet.getLastRow() === 0) {
        promoSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Promo Code Used",
            "Activation Date",
            "Expiry Date",
            "Status",
            "IP Address"
        ]);
        promoSheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#34a853").setFontColor("#ffffff");
        promoSheet.setFrozenRows(1);
        promoSheet.autoResizeColumns(1, 8);
    }

    // Sheet 4: Payment History (All Transactions)
    var paymentSheet = ss.getSheetByName("Payment History") || ss.insertSheet("Payment History");
    if (paymentSheet.getLastRow() === 0) {
        paymentSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Payment Method",
            "Payment Details",
            "Amount (₹)",
            "Transaction ID",
            "Razorpay Order ID",
            "Razorpay Payment ID",
            "Status",
            "IP Address",
            "Error Message"
        ]);
        paymentSheet.getRange(1, 1, 1, 12).setFontWeight("bold").setBackground("#fbbc04").setFontColor("#ffffff");
        paymentSheet.setFrozenRows(1);
        paymentSheet.autoResizeColumns(1, 12);
    }

    // Sheet 5: Failed Payments
    var failedSheet = ss.getSheetByName("Failed Payments") || ss.insertSheet("Failed Payments");
    if (failedSheet.getLastRow() === 0) {
        failedSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Payment Method",
            "Amount (₹)",
            "Razorpay Order ID",
            "Error Message",
            "IP Address"
        ]);
        failedSheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#f44336").setFontColor("#ffffff");
        failedSheet.setFrozenRows(1);
        failedSheet.autoResizeColumns(1, 8);
    }

    // Sheet 6: Account Upgrades
    var upgradeSheet = ss.getSheetByName("Account Upgrades") || ss.insertSheet("Account Upgrades");
    if (upgradeSheet.getLastRow() === 0) {
        upgradeSheet.appendRow([
            "Timestamp",
            "Email",
            "Name",
            "Previous Plan",
            "New Plan",
            "Upgrade Method",
            "Validity Period"
        ]);
        upgradeSheet.getRange(1, 1, 1, 7).setFontWeight("bold").setBackground("#ea4335").setFontColor("#ffffff");
        upgradeSheet.setFrozenRows(1);
        upgradeSheet.autoResizeColumns(1, 7);
    }

    // Sheet 7: Revenue Summary
    var revenueSheet = ss.getSheetByName("Revenue Summary") || ss.insertSheet("Revenue Summary");
    if (revenueSheet.getLastRow() === 0) {
        revenueSheet.appendRow([
            "Date",
            "Total Revenue (₹)",
            "Razorpay Payments",
            "Promo Code Upgrades",
            "Total Pro Users",
            "Active Pro Users",
            "Expired Pro Users"
        ]);
        revenueSheet.getRange(1, 1, 1, 7).setFontWeight("bold").setBackground("#00bcd4").setFontColor("#ffffff");
        revenueSheet.setFrozenRows(1);
        revenueSheet.autoResizeColumns(1, 7);
    }

    Logger.log("✅ All sheets created successfully!");
}

// ─────────────────────────────────────────────────────────────────────────────
// 🔧 HELPER FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

// Calculate expiry date (30 days from activation)
function calculateExpiryDate(activationDate) {
    var date = new Date(activationDate);
    date.setDate(date.getDate() + 30);
    return Utilities.formatDate(date, Session.getScriptTimeZone(), "yyyy-MM-dd");
}

// Calculate days remaining
function calculateDaysRemaining(expiryDate) {
    var today = new Date();
    var expiry = new Date(expiryDate);
    var diffTime = expiry - today;
    var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
}

// Check if plan is active
function isPlanActive(expiryDate) {
    var today = new Date();
    var expiry = new Date(expiryDate);
    return expiry > today ? "ACTIVE" : "EXPIRED";
}

// Format timestamp
function getTimestamp() {
    return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
}

// Get payment method details
function getPaymentMethodDetails(data) {
    if (data.payment_details) {
        return data.payment_details;
    }
    if (data.payment_method) {
        var method = data.payment_method.toLowerCase();
        if (method.includes("card")) return "Credit/Debit Card";
        if (method.includes("upi")) return "UPI";
        if (method.includes("wallet")) return "Wallet";
        if (method.includes("netbanking")) return "Net Banking";
        if (method.includes("promo")) return "Promo Code";
    }
    return "Unknown";
}

// ─────────────────────────────────────────────────────────────────────────────
// 📨 POST REQUEST HANDLER - Receive data from Python backend
// ─────────────────────────────────────────────────────────────────────────────
function doPost(e) {
    var lock = LockService.getScriptLock();
    lock.tryLock(10000);

    try {
        var data = JSON.parse(e.postData.contents);
        var ss = SpreadsheetApp.getActiveSpreadsheet();
        var action = data.action || "pro_upgrade";

        // Extract common data
        var timestamp = data.timestamp || getTimestamp();
        var email = data.email || "";
        var name = data.name || "";
        var ipAddress = data.ip_address || "";
        var userAgent = data.user_agent || "";

        // ═══════════════════════════════════════════════════════════════════════
        // HANDLE USER REGISTRATION
        // ═══════════════════════════════════════════════════════════════════════
        if (action === "register") {
            var userSheet = ss.getSheetByName("User Registrations");
            if (!userSheet) {
                setupSheets();
                userSheet = ss.getSheetByName("User Registrations");
            }

            userSheet.appendRow([
                timestamp,
                email,
                name,
                data.registration_method || "Email",
                data.plan_type || "FREE",
                ipAddress,
                userAgent
            ]);

            return ContentService
                .createTextOutput(JSON.stringify({
                    'result': 'success',
                    'message': 'User registered successfully'
                }))
                .setMimeType(ContentService.MimeType.JSON);
        }

        // ═══════════════════════════════════════════════════════════════════════
        // HANDLE PRO PLAN UPGRADE
        // ═══════════════════════════════════════════════════════════════════════
        if (action === "pro_upgrade" || action === "payment_success") {
            var phone = data.phone || "";
            var paymentMethod = data.payment_method || "Razorpay";
            var paymentDetails = getPaymentMethodDetails(data);
            var amount = data.amount || "0";
            var transactionId = data.transaction_id || "";
            var razorpayOrderId = data.razorpay_order_id || "";
            var razorpayPaymentId = data.razorpay_payment_id || "";
            var promoCode = data.promo_code || "N/A";
            var planType = data.plan_type || "PRO";
            var activationDate = data.activation_date || Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
            var expiryDate = data.expiry_date || calculateExpiryDate(activationDate);

            // Calculate dynamic fields
            var daysRemaining = calculateDaysRemaining(expiryDate);
            var status = isPlanActive(expiryDate);

            // ───────────────────────────────────────────────────────────────────
            // 1️⃣ UPDATE PRO USERS SHEET
            // ───────────────────────────────────────────────────────────────────
            var proSheet = ss.getSheetByName("Pro Users");
            if (!proSheet) {
                setupSheets();
                proSheet = ss.getSheetByName("Pro Users");
            }

            // Check if user already exists
            var proData = proSheet.getDataRange().getValues();
            var userExists = false;
            var userRow = -1;

            for (var i = 1; i < proData.length; i++) {
                if (proData[i][1] === email) { // Column B (Email)
                    userExists = true;
                    userRow = i + 1;
                    break;
                }
            }

            if (userExists) {
                // Update existing user
                proSheet.getRange(userRow, 1, 1, 18).setValues([[
                    timestamp, email, name, phone, paymentMethod, paymentDetails, amount,
                    transactionId, razorpayOrderId, razorpayPaymentId, promoCode,
                    planType, activationDate, expiryDate, daysRemaining, status, ipAddress, userAgent
                ]]);
            } else {
                // Add new user
                proSheet.appendRow([
                    timestamp, email, name, phone, paymentMethod, paymentDetails, amount,
                    transactionId, razorpayOrderId, razorpayPaymentId, promoCode,
                    planType, activationDate, expiryDate, daysRemaining, status, ipAddress, userAgent
                ]);
            }

            // ───────────────────────────────────────────────────────────────────
            // 2️⃣ LOG PROMO CODE USAGE (if applicable)
            // ───────────────────────────────────────────────────────────────────
            if (promoCode !== "N/A" && paymentMethod.toLowerCase().includes("promo")) {
                var promoSheet = ss.getSheetByName("Promo Code History");
                promoSheet.appendRow([
                    timestamp, email, name, promoCode, activationDate, expiryDate, status, ipAddress
                ]);
            }

            // ───────────────────────────────────────────────────────────────────
            // 3️⃣ LOG PAYMENT HISTORY
            // ───────────────────────────────────────────────────────────────────
            var paymentSheet = ss.getSheetByName("Payment History");
            paymentSheet.appendRow([
                timestamp, email, name, paymentMethod, paymentDetails, amount,
                transactionId, razorpayOrderId, razorpayPaymentId, "SUCCESS", ipAddress, ""
            ]);

            // ───────────────────────────────────────────────────────────────────
            // 4️⃣ LOG ACCOUNT UPGRADE
            // ───────────────────────────────────────────────────────────────────
            var upgradeSheet = ss.getSheetByName("Account Upgrades");
            upgradeSheet.appendRow([
                timestamp, email, name, "FREE", planType, paymentMethod, "30 Days"
            ]);

            return ContentService
                .createTextOutput(JSON.stringify({
                    'result': 'success',
                    'message': 'Pro plan activated successfully',
                    'expiry_date': expiryDate,
                    'days_remaining': daysRemaining,
                    'status': status
                }))
                .setMimeType(ContentService.MimeType.JSON);
        }

        // ═══════════════════════════════════════════════════════════════════════
        // HANDLE FAILED PAYMENT
        // ═══════════════════════════════════════════════════════════════════════
        if (action === "payment_failed") {
            var failedSheet = ss.getSheetByName("Failed Payments");
            if (!failedSheet) {
                setupSheets();
                failedSheet = ss.getSheetByName("Failed Payments");
            }

            failedSheet.appendRow([
                timestamp,
                email,
                name,
                data.payment_method || "Razorpay",
                data.amount || "0",
                data.razorpay_order_id || "",
                data.error_message || "Payment failed",
                ipAddress
            ]);

            // Also log in payment history
            var paymentSheet = ss.getSheetByName("Payment History");
            paymentSheet.appendRow([
                timestamp, email, name, data.payment_method || "Razorpay",
                getPaymentMethodDetails(data), data.amount || "0",
                "", data.razorpay_order_id || "", "", "FAILED", ipAddress,
                data.error_message || "Payment failed"
            ]);

            return ContentService
                .createTextOutput(JSON.stringify({
                    'result': 'success',
                    'message': 'Failed payment logged'
                }))
                .setMimeType(ContentService.MimeType.JSON);
        }

        return ContentService
            .createTextOutput(JSON.stringify({
                'result': 'error',
                'message': 'Unknown action: ' + action
            }))
            .setMimeType(ContentService.MimeType.JSON);

    } catch (error) {
        return ContentService
            .createTextOutput(JSON.stringify({
                'result': 'error',
                'error': error.toString()
            }))
            .setMimeType(ContentService.MimeType.JSON);
    } finally {
        lock.releaseLock();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// 📥 GET REQUEST HANDLER - Return active PRO users
// ─────────────────────────────────────────────────────────────────────────────
function doGet(e) {
    try {
        var ss = SpreadsheetApp.getActiveSpreadsheet();
        var action = e.parameter.action || "active";

        // ═══════════════════════════════════════════════════════════════════════
        // GET PRO USERS
        // ═══════════════════════════════════════════════════════════════════════
        if (action === "active" || action === "all" || action === "expired") {
            var proSheet = ss.getSheetByName("Pro Users");

            if (!proSheet) {
                return ContentService
                    .createTextOutput(JSON.stringify({
                        'result': 'error',
                        'message': 'Sheet not found. Run setupSheets() first.'
                    }))
                    .setMimeType(ContentService.MimeType.JSON);
            }

            var rows = proSheet.getDataRange().getValues();
            var activeUsers = [];
            var expiredUsers = [];
            var allUsers = [];

            // Skip header row
            for (var i = 1; i < rows.length; i++) {
                var row = rows[i];
                var email = row[1];
                var name = row[2];
                var planType = row[11];
                var expiryDate = row[13];
                var daysRemaining = calculateDaysRemaining(expiryDate);
                var status = isPlanActive(expiryDate);

                var userObj = {
                    email: email,
                    name: name,
                    plan_type: planType,
                    expiry_date: expiryDate,
                    days_remaining: daysRemaining,
                    status: status
                };

                allUsers.push(userObj);

                if (status === "ACTIVE") {
                    activeUsers.push(userObj);
                } else {
                    expiredUsers.push(userObj);
                }
            }

            if (action === "all") {
                return ContentService
                    .createTextOutput(JSON.stringify(allUsers))
                    .setMimeType(ContentService.MimeType.JSON);
            } else if (action === "expired") {
                return ContentService
                    .createTextOutput(JSON.stringify(expiredUsers))
                    .setMimeType(ContentService.MimeType.JSON);
            } else {
                // Default: return only active users
                return ContentService
                    .createTextOutput(JSON.stringify(activeUsers))
                    .setMimeType(ContentService.MimeType.JSON);
            }
        }

        // ═══════════════════════════════════════════════════════════════════════
        // GET REVENUE STATS
        // ═══════════════════════════════════════════════════════════════════════
        if (action === "revenue") {
            var paymentSheet = ss.getSheetByName("Payment History");
            var proSheet = ss.getSheetByName("Pro Users");

            if (!paymentSheet || !proSheet) {
                return ContentService
                    .createTextOutput(JSON.stringify({
                        'result': 'error',
                        'message': 'Sheets not found'
                    }))
                    .setMimeType(ContentService.MimeType.JSON);
            }

            var paymentData = paymentSheet.getDataRange().getValues();
            var proData = proSheet.getDataRange().getValues();

            var totalRevenue = 0;
            var razorpayCount = 0;
            var promoCount = 0;

            // Calculate revenue (skip header)
            for (var i = 1; i < paymentData.length; i++) {
                if (paymentData[i][9] === "SUCCESS") { // Status column
                    var amount = parseFloat(paymentData[i][5]) || 0;
                    totalRevenue += amount;

                    if (paymentData[i][3].toLowerCase().includes("razorpay")) {
                        razorpayCount++;
                    } else if (paymentData[i][3].toLowerCase().includes("promo")) {
                        promoCount++;
                    }
                }
            }

            // Count active/expired users
            var activeCount = 0;
            var expiredCount = 0;
            for (var i = 1; i < proData.length; i++) {
                var status = isPlanActive(proData[i][13]);
                if (status === "ACTIVE") {
                    activeCount++;
                } else {
                    expiredCount++;
                }
            }

            return ContentService
                .createTextOutput(JSON.stringify({
                    total_revenue: totalRevenue,
                    razorpay_payments: razorpayCount,
                    promo_upgrades: promoCount,
                    total_pro_users: proData.length - 1,
                    active_users: activeCount,
                    expired_users: expiredCount
                }))
                .setMimeType(ContentService.MimeType.JSON);
        }

        return ContentService
            .createTextOutput(JSON.stringify({
                'result': 'error',
                'message': 'Unknown action'
            }))
            .setMimeType(ContentService.MimeType.JSON);

    } catch (error) {
        return ContentService
            .createTextOutput(JSON.stringify({
                'result': 'error',
                'error': error.toString()
            }))
            .setMimeType(ContentService.MimeType.JSON);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// 🔄 AUTO-UPDATE FUNCTION - Run daily to update status
// ─────────────────────────────────────────────────────────────────────────────
function updateAllUserStatus() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var proSheet = ss.getSheetByName("Pro Users");

    if (!proSheet) return;

    var rows = proSheet.getDataRange().getValues();

    for (var i = 1; i < rows.length; i++) {
        var expiryDate = rows[i][13]; // Column N
        var daysRemaining = calculateDaysRemaining(expiryDate);
        var status = isPlanActive(expiryDate);

        // Update columns O and P
        proSheet.getRange(i + 1, 15).setValue(daysRemaining);
        proSheet.getRange(i + 1, 16).setValue(status);

        // Color code based on status
        if (status === "EXPIRED") {
            proSheet.getRange(i + 1, 1, 1, 18).setBackground("#ffebee"); // Light red
        } else if (daysRemaining <= 7) {
            proSheet.getRange(i + 1, 1, 1, 18).setBackground("#fff9c4"); // Light yellow
        } else {
            proSheet.getRange(i + 1, 1, 1, 18).setBackground("#e8f5e9"); // Light green
        }
    }

    Logger.log("✅ User status updated successfully!");
}

// ─────────────────────────────────────────────────────────────────────────────
// 📊 UPDATE REVENUE SUMMARY - Run daily
// ─────────────────────────────────────────────────────────────────────────────
function updateRevenueSummary() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var revenueSheet = ss.getSheetByName("Revenue Summary");
    var paymentSheet = ss.getSheetByName("Payment History");
    var proSheet = ss.getSheetByName("Pro Users");

    if (!revenueSheet || !paymentSheet || !proSheet) return;

    var today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
    var paymentData = paymentSheet.getDataRange().getValues();
    var proData = proSheet.getDataRange().getValues();

    var totalRevenue = 0;
    var razorpayCount = 0;
    var promoCount = 0;

    // Calculate today's revenue
    for (var i = 1; i < paymentData.length; i++) {
        if (paymentData[i][9] === "SUCCESS") {
            var amount = parseFloat(paymentData[i][5]) || 0;
            totalRevenue += amount;

            if (paymentData[i][3].toLowerCase().includes("razorpay")) {
                razorpayCount++;
            } else if (paymentData[i][3].toLowerCase().includes("promo")) {
                promoCount++;
            }
        }
    }

    // Count users
    var activeCount = 0;
    var expiredCount = 0;
    for (var i = 1; i < proData.length; i++) {
        var status = isPlanActive(proData[i][13]);
        if (status === "ACTIVE") {
            activeCount++;
        } else {
            expiredCount++;
        }
    }

    revenueSheet.appendRow([
        today,
        totalRevenue,
        razorpayCount,
        promoCount,
        proData.length - 1,
        activeCount,
        expiredCount
    ]);

    Logger.log("✅ Revenue summary updated!");
}

// ─────────────────────────────────────────────────────────────────────────────
// ⏰ CREATE DAILY TRIGGER - Run this once to auto-update daily
// ─────────────────────────────────────────────────────────────────────────────
function createDailyTrigger() {
    // Delete existing triggers
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
        ScriptApp.deleteTrigger(triggers[i]);
    }

    // Create new daily trigger at 2 AM for status update
    ScriptApp.newTrigger('updateAllUserStatus')
        .timeBased()
        .atHour(2)
        .everyDays(1)
        .create();

    // Create new daily trigger at 3 AM for revenue summary
    ScriptApp.newTrigger('updateRevenueSummary')
        .timeBased()
        .atHour(3)
        .everyDays(1)
        .create();

    Logger.log("✅ Daily triggers created successfully!");
}
