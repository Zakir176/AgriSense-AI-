<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Financial Intelligence</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Revenue tracking, expense management, profit analysis, and income forecasting for
          <span v-if="activeBatchObj" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic text-gray-450">no batch selected</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            placeholder="Select batch..."
            @change="onBatchChange"
          />
        </div>
        <AgriButton
          variant="secondary"
          size="sm"
          :disabled="!selectedBatchId || loading || pdfExporting"
          @click="downloadFinancialPDF"
          title="Download PDF Financial Report"
        >
          <span v-if="pdfExporting" class="material-icons-outlined text-sm mr-1.5 animate-spin">refresh</span>
          <span v-else class="material-icons-outlined text-sm mr-1.5 text-red-500">picture_as_pdf</span>
          <span>{{ pdfExporting ? 'Generating...' : 'Export PDF' }}</span>
        </AgriButton>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">account_balance</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">Select a batch to view financial intelligence</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Revenue, expenses, profit/loss, and income projections are computed per-batch.</p>
    </div>

    <template v-else>

      <!-- ─── Loading State ─── -->
      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <AgriSkeleton v-for="n in 5" :key="n" type="card" height="h-24" />
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AgriSkeleton v-for="n in 2" :key="n" type="chart" />
        </div>
      </div>

      <template v-else>

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!-- Section 1 — Financial Summary KPI Cards                           -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <!-- Total Revenue -->
          <AgriStatCard
            label="Total Revenue"
            :value="summary.total_revenue_zmw"
            :decimals="2"
            prefix="K "
            icon="trending_up"
            icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400"
            :subtext="`${summary.total_birds_sold} birds sold`"
            class="animate-fade-in-up delay-100"
          />

          <!-- Total Expenses -->
          <AgriStatCard
            label="Total Expenses"
            :value="summary.total_expenses_zmw"
            :decimals="2"
            prefix="K "
            icon="receipt_long"
            icon-color-class="bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400"
            :subtext="expenseCategorySummary"
            class="animate-fade-in-up delay-150"
          />

          <!-- Gross Profit / Loss -->
          <AgriStatCard
            label="Gross Profit"
            :value="summary.gross_profit_zmw"
            :decimals="2"
            prefix="K "
            icon="account_balance"
            :icon-color-class="summary.gross_profit_zmw >= 0
              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400'
              : 'bg-red-50 dark:bg-red-950/40 text-red-500 dark:text-red-400'"
            :trend="summary.gross_profit_zmw >= 0 ? 'Profitable' : 'Loss'"
            :trend-direction="summary.gross_profit_zmw >= 0 ? 'up' : 'down'"
            :trend-good="summary.gross_profit_zmw >= 0"
            :subtext="summary.gross_profit_zmw >= 0 ? 'Revenue exceeds costs' : 'Costs exceed revenue'"
            class="animate-fade-in-up delay-200"
          />

          <!-- Avg Price per Bird -->
          <AgriStatCard
            label="Avg Price / Bird"
            :value="summary.avg_price_per_bird_zmw"
            :decimals="2"
            prefix="K "
            icon="sell"
            icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500 dark:text-blue-400"
            :subtext="`Based on ${summary.total_birds_sold} sales`"
            class="animate-fade-in-up delay-250"
          />

          <!-- Profit Margin -->
          <AgriStatCard
            label="Profit Margin"
            :value="summary.profit_margin_pct"
            :decimals="1"
            suffix="%"
            icon="speed"
            :icon-color-class="summary.profit_margin_pct >= 20
              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400'
              : summary.profit_margin_pct >= 0
                ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400'
                : 'bg-red-50 dark:bg-red-950/40 text-red-500 dark:text-red-400'"
            :trend="getMarginLabel(summary.profit_margin_pct)"
            trend-direction="neutral"
            :trend-good="summary.profit_margin_pct >= 20"
            :subtext="`${summary.current_live_count} birds remaining`"
            class="animate-fade-in-up delay-300"
          />
        </div>

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!-- Section 2 — Sales Recording                                       -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <AgriCard class="animate-fade-in-up delay-200">
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-emerald-500 text-lg">point_of_sale</span>
              <h2 class="text-sm font-bold text-gray-800 dark:text-white">Sales History</h2>
              <span class="ml-1 text-xs text-gray-400 dark:text-gray-500">({{ salesEntries.length }} records)</span>
            </div>
            <AgriButton variant="primary" size="sm" @click="showSaleModal = true">
              <span class="material-icons-outlined text-sm mr-1">add</span>
              Log Sale
            </AgriButton>
          </template>

          <AgriTable
            :headers="salesHeaders"
            :items="salesEntries"
            :loading="salesLoading"
            striped
          >
            <template #date="{ item }">
              <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ item.date }}</span>
            </template>
            <template #birds_sold="{ item }">
              <span class="inline-flex items-center gap-1 text-xs font-bold text-gray-800 dark:text-gray-200">
                <span class="material-icons-outlined text-[13px] text-gray-400">egg_alt</span>
                {{ item.birds_sold }}
              </span>
            </template>
            <template #unit_price_zmw="{ item }">
              <span class="text-xs font-semibold tabular-nums">
                {{ item.unit_price_zmw != null ? `K ${item.unit_price_zmw.toFixed(2)}` : '—' }}
              </span>
            </template>
            <template #total_zmw="{ item }">
              <span class="text-xs font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
                {{ item.total_zmw != null ? `K ${item.total_zmw.toFixed(2)}` : '—' }}
              </span>
            </template>
            <template #buyer="{ item }">
              <span class="text-xs text-gray-500 dark:text-gray-400 italic">
                {{ item.buyer || '—' }}
              </span>
            </template>
          </AgriTable>

          <!-- Empty state hint inside the card footer -->
          <template v-if="salesEntries.length === 0 && !salesLoading" #footer>
            <div class="w-full text-center py-2">
              <p class="text-xs text-gray-400 dark:text-gray-500">No sales recorded yet. Use the <strong>Log Sale</strong> button to record your first sale.</p>
            </div>
          </template>
        </AgriCard>

        <!-- Sale Modal -->
        <FlockInventoryModal
          :show="showSaleModal"
          :batch-id="selectedBatchId"
          @close="showSaleModal = false"
          @success="handleSaleSubmit"
        />

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!-- Section 3 — Expense Tracking                                       -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- Expense Table (spans 2 cols on large screens) -->
          <AgriCard class="lg:col-span-2 animate-fade-in-up delay-300">
            <template #header>
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-amber-500 text-lg">receipt_long</span>
                <h2 class="text-sm font-bold text-gray-800 dark:text-white">Expense Log</h2>
                <span class="ml-1 text-xs text-gray-400 dark:text-gray-500">({{ expenseEntries.length }} records)</span>
              </div>
              <AgriButton variant="primary" size="sm" @click="showExpenseModal = true">
                <span class="material-icons-outlined text-sm mr-1">add</span>
                Add Expense
              </AgriButton>
            </template>

            <AgriTable
              :headers="expenseHeaders"
              :items="expenseEntries"
              :loading="expensesLoading"
              striped
            >
              <template #date="{ item }">
                <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ item.date }}</span>
              </template>
              <template #category="{ item }">
                <span
                  class="inline-flex items-center gap-1.5 text-xs font-bold px-2 py-0.5 rounded-lg"
                  :class="expenseCategoryStyle(item.category)"
                >
                  <span class="material-icons-outlined text-[13px]">{{ expenseCategoryIcon(item.category) }}</span>
                  {{ item.category }}
                </span>
              </template>
              <template #description="{ item }">
                <span class="text-xs text-gray-600 dark:text-gray-400">
                  {{ item.description || '—' }}
                </span>
              </template>
              <template #amount_zmw="{ item }">
                <span class="text-xs font-bold tabular-nums text-amber-600 dark:text-amber-400">
                  K {{ item.amount_zmw.toFixed(2) }}
                </span>
              </template>
            </AgriTable>

            <template v-if="expenseEntries.length === 0 && !expensesLoading" #footer>
              <div class="w-full text-center py-2">
                <p class="text-xs text-gray-400 dark:text-gray-500">No expenses logged yet. Use <strong>Add Expense</strong> to start tracking costs.</p>
              </div>
            </template>
          </AgriCard>

          <!-- Expense Breakdown Chart -->
          <AgriCard class="animate-fade-in-up delay-400">
            <template #header>
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-violet-500 text-lg">donut_small</span>
                <h2 class="text-sm font-bold text-gray-800 dark:text-white">By Category</h2>
              </div>
            </template>
            <div class="flex items-center justify-center px-4 pb-2">
              <div v-if="hasExpenseData" class="w-full max-w-[280px] aspect-square">
                <canvas ref="expenseChartCanvas"></canvas>
              </div>
              <div v-else class="py-12 text-center w-full">
                <span class="material-icons-outlined text-3xl text-gray-300 dark:text-gray-700 block mb-2">pie_chart</span>
                <p class="text-xs text-gray-400 dark:text-gray-500">Expense data will appear here once logged.</p>
              </div>
            </div>
            <!-- Category legend -->
            <template v-if="hasExpenseData" #footer>
              <div class="flex flex-wrap gap-3 w-full">
                <div
                  v-for="(amount, cat) in summary.expenses_by_category"
                  :key="cat"
                  class="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400"
                >
                  <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: categoryColor(cat) }"></span>
                  <span class="font-semibold capitalize">{{ cat }}</span>
                  <span class="tabular-nums text-gray-400 dark:text-gray-500">K{{ amount.toFixed(0) }}</span>
                </div>
              </div>
            </template>
          </AgriCard>
        </div>

        <!-- Revenue vs Expenses Trend Chart -->
        <AgriCard class="animate-fade-in-up">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-primary-500 dark:text-primary-400">trending_up</span>
                <h3 class="text-base font-semibold text-gray-800 dark:text-gray-100">
                  Revenue vs Expenses Trend
                </h3>
              </div>
            </div>
          </template>

          <div
            v-if="salesEntries.length === 0 && expenseEntries.length === 0"
            class="h-48 flex items-center justify-center text-sm text-gray-400 dark:text-gray-600 italic"
          >
            No sales or expense data recorded yet
          </div>
          <div v-else class="relative h-64">
            <canvas ref="trendChartCanvas"></canvas>
          </div>
        </AgriCard>

        <!-- Add Expense Modal -->
        <AgriModal
          :show="showExpenseModal"
          title="Log Expense"
          @close="showExpenseModal = false"
        >
          <form @submit.prevent="handleExpenseSubmit" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <AgriInput
                v-model="expenseForm.date"
                type="date"
                label="Date"
                required
                icon="calendar_today"
              />
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Category</label>
                <AgriSelect
                  v-model="expenseForm.category"
                  :options="expenseCategoryOptions"
                  placeholder="Select category..."
                />
              </div>
            </div>

            <AgriInput
              v-model="expenseForm.description"
              type="text"
              label="Description (Optional)"
              placeholder="e.g. 50kg Broiler Starter Feed"
              icon="notes"
            />

            <AgriInput
              v-model.number="expenseForm.amount_zmw"
              type="number"
              label="Amount (ZMW)"
              required
              min="0.01"
              step="0.01"
              placeholder="e.g. 450.00"
              icon="payments"
            />

            <div v-if="expenseError" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
              {{ expenseError }}
            </div>

            <div class="flex space-x-3 pt-4 border-t border-gray-150 dark:border-gray-800">
              <AgriButton type="button" variant="outline" class="flex-1" @click="showExpenseModal = false">Cancel</AgriButton>
              <AgriButton type="submit" variant="primary" class="flex-1" :loading="expenseSubmitting">Save Expense</AgriButton>
            </div>
          </form>
        </AgriModal>

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!-- Section 4 — Income Forecast                                       -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <AgriCard class="animate-fade-in-up delay-400">
          <template #header>
            <div class="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-primary-500 text-lg">insights</span>
                <h2 class="text-sm font-bold text-gray-800 dark:text-white">Income Forecast</h2>
                <span class="text-xs text-gray-400 dark:text-gray-500">(Mortality-Adjusted Projection)</span>
              </div>
              <div class="flex items-center gap-1.5 text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30 px-2.5 py-1 rounded-lg border border-amber-200 dark:border-amber-900/30 font-medium">
                <span class="material-icons-outlined text-sm">info</span>
                Estimate based on current mortality trend
              </div>
            </div>
          </template>

          <div class="p-6 space-y-6">
            <!-- Price Input Row -->
            <div class="max-w-xs">
              <AgriInput
                v-model.number="forecastPrice"
                type="number"
                label="Expected Price per Bird (ZMW)"
                min="0.01"
                step="0.5"
                placeholder="e.g. 85.00"
                icon="payments"
                @input="onForecastPriceInput"
              />
            </div>

            <!-- Forecast KPI Cards Grid -->
            <div v-if="forecastData" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Live Count -->
              <div class="bg-gray-50 dark:bg-darkbg-100/40 p-4 rounded-xl border border-gray-150 dark:border-gray-800">
                <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider block mb-1">Current Live Birds</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ forecastData.current_live_count }}</span>
                  <span class="text-xs text-gray-500">birds</span>
                </div>
              </div>

              <!-- Projected 30-Day Mortality -->
              <div class="bg-gray-50 dark:bg-darkbg-100/40 p-4 rounded-xl border border-gray-150 dark:border-gray-800">
                <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider block mb-1">Projected 30d Mortality</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-2xl font-black text-red-600 dark:text-red-400 tabular-nums">-{{ forecastData.projected_30d_mortality }}</span>
                  <span class="text-xs text-gray-500">birds</span>
                </div>
              </div>

              <!-- Projected Sellable -->
              <div class="bg-gray-50 dark:bg-darkbg-100/40 p-4 rounded-xl border border-gray-150 dark:border-gray-800">
                <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider block mb-1">Projected Sellable</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-2xl font-black text-blue-600 dark:text-blue-400 tabular-nums">{{ forecastData.projected_sellable_birds }}</span>
                  <span class="text-xs text-gray-500">birds</span>
                </div>
              </div>

              <!-- Expected Income -->
              <div class="bg-emerald-50/60 dark:bg-emerald-950/20 p-4 rounded-xl border border-emerald-200 dark:border-emerald-900/30">
                <span class="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider block mb-1">Expected Income</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400 tabular-nums">K {{ forecastData.expected_income_zmw.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="forecastLoading" class="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <AgriSkeleton v-for="n in 4" :key="n" type="card" height="h-20" />
            </div>
          </div>
        </AgriCard>

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!-- Section 5 — Profit & Loss Statement                                -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <AgriCard class="animate-fade-in-up delay-500">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-purple-500 text-lg">assessment</span>
                <h2 class="text-sm font-bold text-gray-800 dark:text-white">Profit & Loss Statement</h2>
                <span class="text-xs text-gray-400 dark:text-gray-500">(Comprehensive Financial Breakdown)</span>
              </div>
              <span
                v-if="plSummary"
                class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg"
                :class="plSummary.is_profitable
                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/30'
                  : 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-400 border border-red-200 dark:border-red-900/30'"
              >
                <span class="material-icons-outlined text-sm">{{ plSummary.is_profitable ? 'trending_up' : 'trending_down' }}</span>
                {{ plSummary.is_profitable ? 'Net Profitable' : 'Net Loss' }}
              </span>
            </div>
          </template>

          <div class="p-6 space-y-6">
            <!-- Tables side by side -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Revenue Table -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                    <span class="material-icons-outlined text-emerald-500 text-sm">arrow_upward</span>
                    Revenue Breakdown (Sales)
                  </h3>
                  <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                    Total: K {{ summary.total_revenue_zmw.toFixed(2) }}
                  </span>
                </div>
                <AgriTable
                  :headers="salesHeaders"
                  :items="salesEntries"
                  :loading="loading"
                  striped
                >
                  <template #date="{ item }">
                    <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ item.date }}</span>
                  </template>
                  <template #birds_sold="{ item }">
                    <span class="text-xs font-bold text-gray-800 dark:text-gray-200">{{ item.birds_sold }}</span>
                  </template>
                  <template #unit_price_zmw="{ item }">
                    <span class="text-xs font-semibold tabular-nums">
                      {{ item.unit_price_zmw != null ? `K ${item.unit_price_zmw.toFixed(2)}` : '—' }}
                    </span>
                  </template>
                  <template #total_zmw="{ item }">
                    <span class="text-xs font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
                      {{ item.total_zmw != null ? `K ${item.total_zmw.toFixed(2)}` : '—' }}
                    </span>
                  </template>
                  <template #buyer="{ item }">
                    <span class="text-xs text-gray-500 dark:text-gray-400 italic">
                      {{ item.buyer || '—' }}
                    </span>
                  </template>
                </AgriTable>
              </div>

              <!-- Expense Table -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                    <span class="material-icons-outlined text-amber-500 text-sm">arrow_downward</span>
                    Expense Breakdown
                  </h3>
                  <span class="text-xs font-bold text-amber-600 dark:text-amber-400 tabular-nums">
                    Total: K {{ summary.total_expenses_zmw.toFixed(2) }}
                  </span>
                </div>
                <AgriTable
                  :headers="expenseHeaders"
                  :items="expenseEntries"
                  :loading="loading"
                  striped
                >
                  <template #date="{ item }">
                    <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ item.date }}</span>
                  </template>
                  <template #category="{ item }">
                    <span
                      class="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-lg capitalize"
                      :class="expenseCategoryStyle(item.category)"
                    >
                      {{ item.category }}
                    </span>
                  </template>
                  <template #description="{ item }">
                    <span class="text-xs text-gray-600 dark:text-gray-400 truncate max-w-[150px] inline-block">
                      {{ item.description || '—' }}
                    </span>
                  </template>
                  <template #amount_zmw="{ item }">
                    <span class="text-xs font-bold tabular-nums text-amber-600 dark:text-amber-400">
                      K {{ item.amount_zmw.toFixed(2) }}
                    </span>
                  </template>
                </AgriTable>
              </div>
            </div>

            <!-- Bottom Highlight Banner for Net Profit / Loss & Profit Per Bird -->
            <div
              v-if="plSummary"
              class="rounded-2xl p-5 border flex flex-col md:flex-row items-center justify-between gap-4"
              :class="plSummary.is_profitable
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-950 dark:text-emerald-100'
                : 'bg-red-500/10 border-red-500/30 text-red-950 dark:text-red-100'"
            >
              <div class="flex items-center gap-4">
                <div
                  class="h-12 w-12 rounded-2xl flex items-center justify-center shrink-0"
                  :class="plSummary.is_profitable ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'"
                >
                  <span class="material-icons-outlined text-2xl">
                    {{ plSummary.is_profitable ? 'payments' : 'money_off' }}
                  </span>
                </div>
                <div>
                  <span class="text-xs font-bold uppercase tracking-wider opacity-75 block">Net Batch {{ plSummary.is_profitable ? 'Profit' : 'Loss' }}</span>
                  <div class="text-3xl font-black tabular-nums tracking-tight">
                    K {{ Math.abs(plSummary.net_profit_zmw).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                  </div>
                </div>
              </div>

              <!-- Sub-metrics pill grid -->
              <div class="flex flex-wrap items-center gap-4 border-t md:border-t-0 md:border-l border-gray-200 dark:border-gray-800 pt-3 md:pt-0 md:pl-6 w-full md:w-auto">
                <div>
                  <span class="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider block">Profit Per Bird Sold</span>
                  <span class="text-lg font-extrabold text-gray-900 dark:text-white tabular-nums">
                    K {{ plSummary.profit_per_bird_zmw.toFixed(2) }} / bird
                  </span>
                </div>
                <div class="h-8 w-px bg-gray-200 dark:border-gray-800 hidden sm:block"></div>
                <div>
                  <span class="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider block">Total Birds Sold</span>
                  <span class="text-lg font-extrabold text-gray-900 dark:text-white tabular-nums">
                    {{ plSummary.total_birds_sold }} birds
                  </span>
                </div>
              </div>
            </div>
          </div>
        </AgriCard>

      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick, onUnmounted } from 'vue'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import logoFullUrl from '../assets/logo_full.png'
import { store } from '../services/store'
import { api } from '../services/api'
import { useAnimations } from '../composables/useAnimations'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// Reusable UI components
import AgriSelect from '../components/ui/AgriSelect.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriSkeleton from '../components/ui/AgriSkeleton.vue'
import AgriCard from '../components/ui/AgriCard.vue'
import AgriTable from '../components/ui/AgriTable.vue'
import AgriButton from '../components/ui/AgriButton.vue'
import AgriModal from '../components/ui/AgriModal.vue'
import AgriInput from '../components/ui/AgriInput.vue'
import FlockInventoryModal from '../components/FlockInventoryModal.vue'

const { getStaggerDelayClass } = useAnimations()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const loading = ref(false)
const pdfExporting = ref(false)

const summary = ref({
  total_revenue_zmw: 0,
  total_birds_sold: 0,
  avg_price_per_bird_zmw: 0,
  total_expenses_zmw: 0,
  expenses_by_category: {},
  gross_profit_zmw: 0,
  profit_margin_pct: 0,
  current_live_count: 0
})

// Section 2 — Sales
const showSaleModal = ref(false)
const salesLoading = ref(false)
const salesEntries = ref([])
const salesHeaders = [
  { text: 'Date', value: 'date', sortable: true },
  { text: 'Birds Sold', value: 'birds_sold', align: 'right', sortable: true },
  { text: 'Unit Price', value: 'unit_price_zmw', align: 'right', sortable: true },
  { text: 'Total (ZMW)', value: 'total_zmw', align: 'right', sortable: true },
  { text: 'Buyer', value: 'buyer' }
]

// Section 3 — Expenses
const showExpenseModal = ref(false)
const expensesLoading = ref(false)
const expenseSubmitting = ref(false)
const expenseError = ref('')
const expenseEntries = ref([])
const expenseChartCanvas = ref(null)
let expenseChartInstance = null
const trendChartCanvas = ref(null)
let trendChartInstance = null

const expenseHeaders = [
  { text: 'Date', value: 'date', sortable: true },
  { text: 'Category', value: 'category', sortable: true },
  { text: 'Description', value: 'description' },
  { text: 'Amount (ZMW)', value: 'amount_zmw', align: 'right', sortable: true }
]

const expenseCategoryOptions = [
  { value: 'feed', label: 'Feed' },
  { value: 'medication', label: 'Medication' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'labour', label: 'Labour' },
  { value: 'other', label: 'Other' }
]

const expenseForm = ref({
  date: new Date().toISOString().split('T')[0],
  category: 'feed',
  description: '',
  amount_zmw: null
})

// Section 4 — Income Forecast
const forecastPrice = ref(85)
const forecastData = ref(null)
const forecastLoading = ref(false)
let forecastTimeout = null

// Section 5 — Profit & Loss Summary
const plSummary = ref(null)

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const batchOptions = computed(() => {
  return store.batchesList.map(b => ({
    label: `#${b.id} — ${b.breed} (${b.status})`,
    value: b.id
  }))
})



const expenseCategorySummary = computed(() => {
  const cats = summary.value.expenses_by_category
  const keys = Object.keys(cats)
  if (keys.length === 0) return 'No expenses logged'
  return keys.map(k => `${k}: K${cats[k].toFixed(0)}`).join(', ')
})

const hasExpenseData = computed(() => {
  return Object.keys(summary.value.expenses_by_category).length > 0
})

// ── Helpers ────────────────────────────────
const getMarginLabel = (pct) => {
  if (pct >= 30) return 'Excellent'
  if (pct >= 20) return 'Healthy'
  if (pct >= 10) return 'Moderate'
  if (pct >= 0) return 'Low'
  return 'Negative'
}

const CATEGORY_COLORS = {
  feed: '#f59e0b',
  medication: '#ef4444',
  equipment: '#3b82f6',
  labour: '#8b5cf6',
  other: '#6b7280'
}

const categoryColor = (cat) => CATEGORY_COLORS[cat] || CATEGORY_COLORS.other

const expenseCategoryIcon = (cat) => {
  const icons = { feed: 'grass', medication: 'vaccines', equipment: 'construction', labour: 'engineering', other: 'more_horiz' }
  return icons[cat] || 'more_horiz'
}

const expenseCategoryStyle = (cat) => {
  const styles = {
    feed: 'bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400',
    medication: 'bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400',
    equipment: 'bg-blue-50 text-blue-700 dark:bg-blue-950/30 dark:text-blue-400',
    labour: 'bg-violet-50 text-violet-700 dark:bg-violet-950/30 dark:text-violet-400',
    other: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
  return styles[cat] || styles.other
}

// ── Data Loading ───────────────────────────
const loadFinancialData = async () => {
  if (!selectedBatchId.value) return
  loading.value = true
  try {
    const batchId = selectedBatchId.value
    const [summaryData, plData] = await Promise.all([
      api.financial.getSummary(batchId),
      api.financial.getProfitLoss(batchId)
    ])
    summary.value = summaryData
    salesEntries.value = plData.revenue_entries || []
    expenseEntries.value = plData.expense_entries || []
    plSummary.value = plData.summary || null
    await loadForecastData()
    await nextTick()
    renderExpenseChart()
    renderTrendChart()
  } catch (err) {
    console.error('Failed to load financial data:', err)
  } finally {
    loading.value = false
  }
}

const handleSaleSubmit = async (payload) => {
  try {
    await api.inventory.create(selectedBatchId.value, payload)
    showSaleModal.value = false
    // Refresh all financial data
    await loadFinancialData()
  } catch (err) {
    console.error('Failed to record sale:', err)
  }
}

const handleExpenseSubmit = async () => {
  if (!expenseForm.value.amount_zmw || expenseForm.value.amount_zmw <= 0) {
    expenseError.value = 'Amount must be greater than 0'
    return
  }
  if (!expenseForm.value.category) {
    expenseError.value = 'Please select a category'
    return
  }
  expenseSubmitting.value = true
  expenseError.value = ''
  try {
    await api.financial.createExpense(selectedBatchId.value, {
      date: expenseForm.value.date,
      category: expenseForm.value.category,
      description: expenseForm.value.description || null,
      amount_zmw: expenseForm.value.amount_zmw
    })
    showExpenseModal.value = false
    // Reset form
    expenseForm.value = {
      date: new Date().toISOString().split('T')[0],
      category: 'feed',
      description: '',
      amount_zmw: null
    }
    await loadFinancialData()
  } catch (err) {
    expenseError.value = err.message || 'Failed to save expense'
  } finally {
    expenseSubmitting.value = false
  }
}

// ── Expense Chart ──────────────────────────
const renderExpenseChart = () => {
  if (expenseChartInstance) expenseChartInstance.destroy()
  if (!expenseChartCanvas.value) return

  const cats = summary.value.expenses_by_category
  const labels = Object.keys(cats)
  const data = Object.values(cats)
  if (labels.length === 0) return

  const isDark = document.documentElement.classList.contains('dark')

  expenseChartInstance = new Chart(expenseChartCanvas.value, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
      datasets: [{
        data,
        backgroundColor: labels.map(l => categoryColor(l)),
        borderWidth: 2,
        borderColor: isDark ? '#1b1b1e' : '#ffffff',
        hoverBorderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '65%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: isDark ? '#27272a' : '#ffffff',
          titleColor: isDark ? '#e5e7eb' : '#111827',
          bodyColor: isDark ? '#9ca3af' : '#6b7280',
          borderColor: isDark ? '#3f3f46' : '#e5e7eb',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 10,
          titleFont: { family: 'Inter', weight: 'bold', size: 12 },
          bodyFont: { family: 'Inter', size: 11 },
          callbacks: {
            label: (ctx) => ` K ${ctx.parsed.toFixed(2)}`
          }
        }
      }
    }
  })
}

// ── Revenue vs Expenses Trend Chart ────────────
const renderTrendChart = () => {
  if (trendChartInstance) trendChartInstance.destroy()
  if (!trendChartCanvas.value) return
  if (salesEntries.value.length === 0 && expenseEntries.value.length === 0) return

  const isDark = document.documentElement.classList.contains('dark')

  // Collect all unique dates from both sales and expenses, sorted ascending
  const allDates = [...new Set([
    ...salesEntries.value.map(s => s.date),
    ...expenseEntries.value.map(e => e.date)
  ])].sort()

  if (allDates.length === 0) return

  // Build revenue per date (sum all sales on same date)
  const revenueByDate = {}
  salesEntries.value.forEach(s => {
    revenueByDate[s.date] = (revenueByDate[s.date] || 0) + (s.total_zmw || 0)
  })

  // Build expenses per date (sum all expenses on same date)
  const expenseByDate = {}
  expenseEntries.value.forEach(e => {
    expenseByDate[e.date] = (expenseByDate[e.date] || 0) + (e.amount_zmw || 0)
  })

  // Build cumulative profit/loss line
  let cumulative = 0
  const cumulativeData = allDates.map(date => {
    cumulative += (revenueByDate[date] || 0) - (expenseByDate[date] || 0)
    return cumulative
  })

  const labels = allDates.map(d => new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }))

  trendChartInstance = new Chart(trendChartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Revenue (ZMW)',
          data: allDates.map(d => revenueByDate[d] || 0),
          borderColor: '#16a34a',
          backgroundColor: 'rgba(22,163,74,0.08)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: false,
          tension: 0.3
        },
        {
          label: 'Expenses (ZMW)',
          data: allDates.map(d => expenseByDate[d] || 0),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239,68,68,0.08)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: false,
          tension: 0.3
        },
        {
          label: 'Cumulative P&L (ZMW)',
          data: cumulativeData,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          borderWidth: 2,
          borderDash: [5, 4],
          pointRadius: 3,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: isDark ? '#9ca3af' : '#6b7280',
            font: { size: 11 },
            boxWidth: 12,
            padding: 16
          }
        },
        tooltip: {
          backgroundColor: isDark ? '#27272a' : '#ffffff',
          titleColor: isDark ? '#e5e7eb' : '#111827',
          bodyColor: isDark ? '#9ca3af' : '#6b7280',
          borderColor: isDark ? '#3f3f46' : '#e5e7eb',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 10,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ZMW ${ctx.parsed.y.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: isDark ? '#27272a' : '#f3f4f6' },
          ticks: { color: isDark ? '#6b7280' : '#9ca3af', font: { size: 10 } }
        },
        y: {
          grid: { color: isDark ? '#27272a' : '#f3f4f6' },
          ticks: {
            color: isDark ? '#6b7280' : '#9ca3af',
            font: { size: 10 },
            callback: (v) => `ZMW ${v}`
          }
        }
      }
    }
  })
}

const loadForecastData = async () => {
  if (!selectedBatchId.value || !forecastPrice.value || forecastPrice.value <= 0) return
  forecastLoading.value = true
  try {
    const res = await api.financial.getForecast(selectedBatchId.value, forecastPrice.value)
    forecastData.value = res
  } catch (err) {
    console.error('Failed to load income forecast:', err)
  } finally {
    forecastLoading.value = false
  }
}

const onForecastPriceInput = () => {
  if (forecastTimeout) clearTimeout(forecastTimeout)
  forecastTimeout = setTimeout(() => {
    loadForecastData()
  }, 300)
}

const onBatchChange = () => {
  loadFinancialData()
}

// ── Watchers ──────────────────────────────
watch(() => selectedBatchId.value, (newVal) => {
  if (newVal) loadFinancialData()
})

// ── Lifecycle ─────────────────────────────
onMounted(async () => {
  // Auto-select first active batch if available
  if (store.batchesList.length > 0) {
    const active = store.batchesList.find(b => b.status === 'active')
    if (active) {
      selectedBatchId.value = active.id
    }
  }
})

// ── PDF Export Functionality ────────────────
const getBase64ImageFromUrl = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0)
      const dataURL = canvas.toDataURL('image/png')
      resolve(dataURL)
    }
    img.onerror = (err) => reject(err)
    img.src = url
  })
}

const downloadFinancialPDF = async () => {
  if (!selectedBatchId.value) return
  pdfExporting.value = true
  try {
    const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
    const pageWidth = doc.internal.pageSize.getWidth()

    // 1. Load Logo Image
    let logoBase64 = null
    try {
      logoBase64 = await getBase64ImageFromUrl(logoFullUrl)
    } catch (e) {
      console.warn('Could not load logo image for PDF:', e)
    }

    // 2. Header Block with Logo
    let headerY = 12
    if (logoBase64) {
      // Add logo at top left (width: 44mm, height: 14mm)
      doc.addImage(logoBase64, 'PNG', 14, headerY, 44, 14)
    } else {
      doc.setFont('helvetica', 'bold')
      doc.setFontSize(18)
      doc.setTextColor(22, 163, 74)
      doc.text('AgriSense AI', 14, headerY + 10)
    }

    // Header Right Meta Information
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(13)
    doc.setTextColor(30, 41, 59)
    doc.text('FINANCIAL INTELLIGENCE REPORT', pageWidth - 14, headerY + 5, { align: 'right' })

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.setTextColor(100, 116, 139)
    const batchLabel = activeBatchObj.value
      ? `Batch #${activeBatchObj.value.id} (${activeBatchObj.value.breed})`
      : `Batch #${selectedBatchId.value}`
    const currentDate = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })

    doc.text(`Target Batch: ${batchLabel}`, pageWidth - 14, headerY + 10, { align: 'right' })
    doc.text(`Generated: ${currentDate} | Farm: Prime Nest Poultry`, pageWidth - 14, headerY + 15, { align: 'right' })

    // Green Divider Line
    headerY += 19
    doc.setDrawColor(22, 163, 74)
    doc.setLineWidth(0.8)
    doc.line(14, headerY, pageWidth - 14, headerY)

    let currentY = headerY + 8

    // 3. Executive Financial KPI Overview
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(15, 23, 42)
    doc.text('1. Executive Financial Overview', 14, currentY)
    currentY += 4

    const summaryBoxWidth = (pageWidth - 28 - 9) / 4
    const boxHeight = 16

    const kpis = [
      { label: 'TOTAL REVENUE', val: `K ${summary.value.total_revenue_zmw.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, sub: `${summary.value.total_birds_sold} birds sold` },
      { label: 'TOTAL EXPENSES', val: `K ${summary.value.total_expenses_zmw.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, sub: `${Object.keys(summary.value.expenses_by_category).length} categories` },
      { label: 'GROSS PROFIT', val: `K ${summary.value.gross_profit_zmw.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, sub: summary.value.gross_profit_zmw >= 0 ? 'Profitable' : 'Loss' },
      { label: 'PROFIT MARGIN', val: `${summary.value.profit_margin_pct.toFixed(1)}%`, sub: getMarginLabel(summary.value.profit_margin_pct) }
    ]

    kpis.forEach((kpi, idx) => {
      const boxX = 14 + idx * (summaryBoxWidth + 3)
      doc.setFillColor(248, 250, 252)
      doc.setDrawColor(226, 232, 240)
      doc.setLineWidth(0.3)
      doc.roundedRect(boxX, currentY, summaryBoxWidth, boxHeight, 2, 2, 'FD')

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(6.5)
      doc.setTextColor(100, 116, 139)
      doc.text(kpi.label, boxX + 3, currentY + 4.5)

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(9.5)
      doc.setTextColor(15, 23, 42)
      doc.text(kpi.val, boxX + 3, currentY + 10)

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(6.5)
      doc.setTextColor(kpi.sub === 'Loss' ? 225 : 100, kpi.sub === 'Loss' ? 29 : 116, kpi.sub === 'Loss' ? 72 : 139)
      doc.text(kpi.sub, boxX + 3, currentY + 14)
    })

    currentY += boxHeight + 8

    // 4. Sales History Table
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(15, 23, 42)
    doc.text(`2. Sales & Revenue Log (${salesEntries.value.length} Records)`, 14, currentY)
    currentY += 3

    const salesRows = salesEntries.value.map(s => [
      s.date || '—',
      `${s.birds_sold} birds`,
      `K ${s.unit_price_zmw.toFixed(2)}`,
      `K ${s.total_zmw.toFixed(2)}`,
      s.buyer || '—'
    ])

    autoTable(doc, {
      startY: currentY,
      head: [['Date', 'Birds Sold', 'Unit Price (ZMW)', 'Total Revenue (ZMW)', 'Buyer / Notes']],
      body: salesRows.length > 0 ? salesRows : [['—', 'No sales logged', '—', '—', '—']],
      theme: 'grid',
      headStyles: { fillColor: [22, 163, 74], textColor: 255, fontSize: 8, fontStyle: 'bold' },
      bodyStyles: { fontSize: 8, textColor: [30, 41, 59] },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      columnStyles: { 3: { halign: 'right', fontStyle: 'bold' } },
      margin: { left: 14, right: 14 }
    })

    currentY = doc.lastAutoTable.finalY + 8

    if (currentY > 230) {
      doc.addPage()
      currentY = 16
    }

    // 5. Expense Breakdown Table
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(15, 23, 42)
    doc.text(`3. Expense Breakdown Log (${expenseEntries.value.length} Records)`, 14, currentY)
    currentY += 3

    const expenseRows = expenseEntries.value.map(e => [
      e.date || '—',
      (e.category || 'other').toUpperCase(),
      e.description || '—',
      `K ${e.amount_zmw.toFixed(2)}`
    ])

    autoTable(doc, {
      startY: currentY,
      head: [['Date', 'Category', 'Description', 'Amount (ZMW)']],
      body: expenseRows.length > 0 ? expenseRows : [['—', 'No expenses logged', '—', '—']],
      theme: 'grid',
      headStyles: { fillColor: [71, 85, 105], textColor: 255, fontSize: 8, fontStyle: 'bold' },
      bodyStyles: { fontSize: 8, textColor: [30, 41, 59] },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      columnStyles: { 3: { halign: 'right', fontStyle: 'bold' } },
      margin: { left: 14, right: 14 }
    })

    currentY = doc.lastAutoTable.finalY + 8

    if (currentY > 240) {
      doc.addPage()
      currentY = 16
    }

    // 6. Net Profit / Loss Banner
    if (plSummary.value) {
      const isProfitable = plSummary.value.is_profitable
      doc.setFillColor(isProfitable ? 240 : 254, isProfitable ? 253 : 242, isProfitable ? 244 : 242)
      doc.setDrawColor(isProfitable ? 187 : 254, isProfitable ? 247 : 202, isProfitable ? 208 : 202)
      doc.roundedRect(14, currentY, pageWidth - 28, 16, 2, 2, 'FD')

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(9)
      doc.setTextColor(isProfitable ? 21 : 153, isProfitable ? 128 : 27, isProfitable ? 61 : 27)
      doc.text(`BATCH NET ${isProfitable ? 'PROFIT' : 'LOSS'}: K ${Math.abs(plSummary.value.net_profit_zmw).toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 18, currentY + 7)

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(8)
      doc.text(`Profit Per Bird Sold: K ${plSummary.value.profit_per_bird_zmw.toFixed(2)} / bird | Total Birds Sold: ${plSummary.value.total_birds_sold}`, 18, currentY + 12)
    }

    // Page numbering and footer
    const pageCount = doc.internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(8)
      doc.setTextColor(148, 163, 184)
      doc.text(`AgriSense AI · Confidential Farm Financial Intelligence Report`, 14, 287)
      doc.text(`Page ${i} of ${pageCount}`, pageWidth - 14, 287, { align: 'right' })
    }

    const filename = `AgriSense_Financial_Report_Batch_${selectedBatchId.value}_${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(filename)
  } catch (err) {
    console.error('Failed to generate PDF:', err)
  } finally {
    pdfExporting.value = false
  }
}

onUnmounted(() => {
  if (expenseChartInstance) expenseChartInstance.destroy()
  if (trendChartInstance) trendChartInstance.destroy()
})
</script>
