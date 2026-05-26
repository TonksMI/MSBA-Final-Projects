# CPSC 540 HW1 - Generate Exploratory Plots
# This script creates all key visualizations for the homework analysis

# Set working directory
setwd("/Users/matthewtonks/Repositories/CPSC 540/Assignments/HW 1")

# Load required packages
library(tidyverse)
library(MASS)

# Set seed for reproducibility
set.seed(1818)

# Create output directory for plots
if(!dir.exists("plots")) {
  dir.create("plots")
}

# Load data
cat("Loading data...\n")
data <- read.csv("marketingcampaign.csv")

# Convert categorical variables to factors
data <- data %>%
  mutate(
    gender = factor(gender),
    campaign_variant = factor(campaign_variant, levels = c("A", "B", "C")),
    ad_source = factor(ad_source),
    email_signup = factor(email_signup)
  )

cat("Data dimensions:", nrow(data), "rows,", ncol(data), "columns\n")
cat("Summary statistics:\n")
print(summary(data))

# ===== EXPLORATORY PLOTS =====

cat("\nGenerating exploratory plots...\n")

# 1. Distribution of Past Purchases
p1 <- ggplot(data, aes(x = past_purchases)) +
  geom_histogram(bins = 30, fill = "steelblue", color = "black", alpha = 0.7) +
  geom_vline(aes(xintercept = mean(past_purchases)),
             color = "red", linetype = "dashed", size = 1) +
  labs(title = "Distribution of Past Purchases",
       subtitle = paste("Mean =", round(mean(data$past_purchases), 2)),
       x = "Past Purchases", y = "Count") +
  theme_minimal()
ggsave("plots/01_past_purchases_distribution.png", p1, width = 10, height = 6)

# 2. Distribution of Campaign Spend
p2 <- ggplot(data, aes(x = campaign_spend)) +
  geom_histogram(bins = 30, fill = "coral", color = "black", alpha = 0.7) +
  geom_vline(aes(xintercept = mean(campaign_spend)),
             color = "red", linetype = "dashed", size = 1) +
  labs(title = "Distribution of Campaign Spend",
       subtitle = paste("Mean = $", round(mean(data$campaign_spend), 2)),
       x = "Campaign Spend ($)", y = "Count") +
  theme_minimal()
ggsave("plots/02_campaign_spend_distribution.png", p2, width = 10, height = 6)

# 3. Distribution of Age
p3 <- ggplot(data, aes(x = age)) +
  geom_histogram(bins = 30, fill = "forestgreen", color = "black", alpha = 0.7) +
  geom_vline(aes(xintercept = mean(age)),
             color = "red", linetype = "dashed", size = 1) +
  labs(title = "Distribution of Age",
       subtitle = paste("Mean =", round(mean(data$age), 2)),
       x = "Age", y = "Count") +
  theme_minimal()
ggsave("plots/03_age_distribution.png", p3, width = 10, height = 6)

# ===== QUESTION 1 PLOTS =====

cat("Generating Question 1 analysis plots...\n")

# 4. Past Purchases by Gender
p4 <- ggplot(data, aes(x = gender, y = past_purchases, fill = gender)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.05, size = 0.5) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3,
               fill = "red", color = "darkred") +
  labs(title = "Past Purchases by Gender",
       subtitle = "Red diamond = mean",
       x = "Gender", y = "Past Purchases") +
  theme_minimal() +
  theme(legend.position = "none")
ggsave("plots/04_purchases_by_gender.png", p4, width = 10, height = 6)

# Calculate and print means
cat("\nMean past purchases by gender:\n")
gender_stats <- data %>%
  group_by(gender) %>%
  summarise(
    mean_purchases = mean(past_purchases),
    median_purchases = median(past_purchases),
    n = n()
  )
print(gender_stats)

# 5. Past Purchases by Age
p5 <- ggplot(data, aes(x = age, y = past_purchases)) +
  geom_point(alpha = 0.3, color = "steelblue") +
  geom_smooth(method = "loess", color = "red", size = 1.5, se = TRUE) +
  labs(title = "Past Purchases vs Age",
       subtitle = "Smoothed trend line with 95% confidence band",
       x = "Age", y = "Past Purchases") +
  theme_minimal()
ggsave("plots/05_purchases_by_age.png", p5, width = 10, height = 6)

# 6. Past Purchases by Email Signup
p6 <- ggplot(data, aes(x = email_signup, y = past_purchases, fill = email_signup)) +
  geom_boxplot(alpha = 0.7) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3,
               fill = "red", color = "darkred") +
  scale_fill_manual(values = c("TRUE" = "darkgreen", "FALSE" = "darkred")) +
  labs(title = "Past Purchases by Email Signup Status",
       subtitle = "Red diamond = mean",
       x = "Email Signup", y = "Past Purchases") +
  theme_minimal() +
  theme(legend.position = "none")
ggsave("plots/06_purchases_by_email.png", p6, width = 10, height = 6)

# Calculate and print means
cat("\nMean past purchases by email signup:\n")
email_stats <- data %>%
  group_by(email_signup) %>%
  summarise(
    mean_purchases = mean(past_purchases),
    median_purchases = median(past_purchases),
    n = n()
  )
print(email_stats)

# 7. Past Purchases by Ad Source
p7 <- ggplot(data, aes(x = fct_reorder(ad_source, past_purchases),
                        y = past_purchases, fill = ad_source)) +
  geom_boxplot(alpha = 0.7) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3,
               fill = "red", color = "darkred") +
  labs(title = "Past Purchases by Ad Source",
       subtitle = "Ordered by median purchases",
       x = "Ad Source", y = "Past Purchases") +
  theme_minimal() +
  theme(legend.position = "none", axis.text.x = element_text(angle = 45, hjust = 1))
ggsave("plots/07_purchases_by_ad_source.png", p7, width = 10, height = 6)

# Calculate and print means
cat("\nMean past purchases by ad source:\n")
ad_stats <- data %>%
  group_by(ad_source) %>%
  summarise(
    mean_purchases = mean(past_purchases),
    median_purchases = median(past_purchases),
    n = n()
  ) %>%
  arrange(desc(mean_purchases))
print(ad_stats)

# ===== QUESTION 2 PLOTS =====

cat("\nGenerating Question 2 analysis plots...\n")

# 8. Campaign Spend by Variant
p8 <- ggplot(data, aes(x = campaign_variant, y = campaign_spend, fill = campaign_variant)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.05, size = 0.5) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3,
               fill = "red", color = "darkred") +
  scale_fill_manual(values = c("A" = "#E69F00", "B" = "#56B4E9", "C" = "#009E73")) +
  labs(title = "Campaign Spend by Variant",
       subtitle = "Red diamond = mean; A=Original, B=Be Well, C=Mental Health",
       x = "Campaign Variant", y = "Campaign Spend ($)") +
  theme_minimal() +
  theme(legend.position = "none")
ggsave("plots/08_spend_by_variant.png", p8, width = 10, height = 6)

# Calculate summary statistics
cat("\nCampaign spend by variant:\n")
variant_stats <- data %>%
  group_by(campaign_variant) %>%
  summarise(
    n = n(),
    mean_spend = mean(campaign_spend),
    median_spend = median(campaign_spend),
    sd_spend = sd(campaign_spend),
    total_spend = sum(campaign_spend)
  ) %>%
  arrange(desc(mean_spend))
print(variant_stats)

# 9. Mean Campaign Spend by Variant with Error Bars
spend_summary <- data %>%
  group_by(campaign_variant) %>%
  summarise(
    mean_spend = mean(campaign_spend),
    se = sd(campaign_spend) / sqrt(n())
  )

p9 <- ggplot(spend_summary, aes(x = campaign_variant, y = mean_spend, fill = campaign_variant)) +
  geom_col(alpha = 0.7, color = "black") +
  geom_errorbar(aes(ymin = mean_spend - 1.96*se, ymax = mean_spend + 1.96*se),
                width = 0.2, size = 1) +
  geom_text(aes(label = paste0("$", round(mean_spend, 2))), vjust = -2.5, size = 5) +
  scale_fill_manual(values = c("A" = "#E69F00", "B" = "#56B4E9", "C" = "#009E73")) +
  labs(title = "Mean Campaign Spend by Variant (95% CI)",
       subtitle = "Error bars show 95% confidence intervals",
       x = "Campaign Variant", y = "Mean Campaign Spend ($)") +
  theme_minimal() +
  theme(legend.position = "none")
ggsave("plots/09_mean_spend_by_variant.png", p9, width = 10, height = 6)

# 10. Campaign Spend by Variant and Gender
p10 <- ggplot(data, aes(x = campaign_variant, y = campaign_spend, fill = gender)) +
  geom_boxplot(alpha = 0.7) +
  labs(title = "Campaign Spend by Variant and Gender",
       x = "Campaign Variant", y = "Campaign Spend ($)",
       fill = "Gender") +
  theme_minimal()
ggsave("plots/10_spend_by_variant_and_gender.png", p10, width = 10, height = 6)

# 11. Campaign Spend by Variant and Email Signup
p11 <- ggplot(data, aes(x = campaign_variant, y = campaign_spend, fill = email_signup)) +
  geom_boxplot(alpha = 0.7) +
  scale_fill_manual(values = c("TRUE" = "darkgreen", "FALSE" = "darkred")) +
  labs(title = "Campaign Spend by Variant and Email Signup",
       x = "Campaign Variant", y = "Campaign Spend ($)",
       fill = "Email Signup") +
  theme_minimal()
ggsave("plots/11_spend_by_variant_and_email.png", p11, width = 10, height = 6)

# ===== STATISTICAL MODELS =====

cat("\n===== QUESTION 1 ANALYSIS =====\n")

# Check for overdispersion
mean_purchases <- mean(data$past_purchases)
var_purchases <- var(data$past_purchases)
cat("\nPast Purchases - Overdispersion Check:\n")
cat("Mean:", mean_purchases, "\n")
cat("Variance:", var_purchases, "\n")
cat("Variance/Mean Ratio:", var_purchases / mean_purchases, "\n")

if(var_purchases / mean_purchases > 2) {
  cat("→ Overdispersion detected. Using Negative Binomial regression.\n\n")

  # Fit Negative Binomial model
  negbin_model <- glm.nb(past_purchases ~ age + gender + email_signup + ad_source,
                         data = data)

  cat("Negative Binomial Model Summary:\n")
  print(summary(negbin_model))

  # Get exponentiated coefficients (Incident Rate Ratios)
  coef_table <- as.data.frame(summary(negbin_model)$coefficients)
  coef_table$IRR <- exp(coef_table$Estimate)
  coef_table$term <- rownames(coef_table)

  cat("\nIncident Rate Ratios (IRR):\n")
  print(coef_table[, c("term", "IRR", "Pr(>|z|)")])

  # 12. Coefficient plot
  coef_plot_data <- coef_table %>%
    filter(term != "(Intercept)") %>%
    mutate(
      conf.low = exp(Estimate - 1.96 * `Std. Error`),
      conf.high = exp(Estimate + 1.96 * `Std. Error`)
    )

  p12 <- ggplot(coef_plot_data, aes(x = IRR, y = reorder(term, IRR))) +
    geom_vline(xintercept = 1, linetype = "dashed", color = "red", size = 1) +
    geom_point(size = 4, color = "steelblue") +
    geom_errorbarh(aes(xmin = conf.low, xmax = conf.high), height = 0.2, size = 1) +
    labs(
      title = "Incident Rate Ratios for Past Purchases",
      subtitle = "Negative Binomial Regression (95% CI)",
      x = "Incident Rate Ratio (IRR)",
      y = "Predictor"
    ) +
    theme_minimal() +
    theme(axis.text.y = element_text(size = 10))
  ggsave("plots/12_q1_coefficient_plot.png", p12, width = 10, height = 6)

} else {
  cat("→ No overdispersion. Using Poisson regression.\n\n")
}

cat("\n===== QUESTION 2 ANALYSIS =====\n")

# Fit linear regression model
linear_model <- lm(campaign_spend ~ campaign_variant + age + gender +
                   past_purchases + email_signup + ad_source,
                   data = data)

cat("\nLinear Model Summary:\n")
print(summary(linear_model))

# Extract campaign variant coefficients
coef_summary <- as.data.frame(summary(linear_model)$coefficients)
coef_summary$term <- rownames(coef_summary)

cat("\nCampaign Variant Effects:\n")
variant_coefs <- coef_summary[grep("campaign_variant", coef_summary$term), ]
print(variant_coefs[, c("term", "Estimate", "Std. Error", "Pr(>|t|)")])

# 13. Campaign variant coefficient plot
variant_plot_data <- variant_coefs %>%
  mutate(
    conf.low = Estimate - 1.96 * `Std. Error`,
    conf.high = Estimate + 1.96 * `Std. Error`
  )

if(nrow(variant_plot_data) > 0) {
  p13 <- ggplot(variant_plot_data, aes(x = Estimate, y = term)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "red", size = 1) +
    geom_point(size = 4, color = "steelblue") +
    geom_errorbarh(aes(xmin = conf.low, xmax = conf.high), height = 0.2, size = 1) +
    labs(
      title = "Campaign Variant Effects on Spend",
      subtitle = "Linear Regression Coefficients (95% CI) - Relative to Variant A",
      x = "Effect on Campaign Spend ($)",
      y = "Campaign Variant"
    ) +
    theme_minimal()
  ggsave("plots/13_q2_coefficient_plot.png", p13, width = 10, height = 6)
}

# ANOVA for campaign variants
cat("\nOne-way ANOVA for Campaign Variants:\n")
anova_result <- aov(campaign_spend ~ campaign_variant, data = data)
print(summary(anova_result))

# Tukey HSD for pairwise comparisons
cat("\nTukey's HSD Pairwise Comparisons:\n")
tukey_result <- TukeyHSD(anova_result)
print(tukey_result)

# 14. Predicted spend by variant
predicted_by_variant <- data %>%
  mutate(predicted = predict(linear_model, type = "response")) %>%
  group_by(campaign_variant) %>%
  summarise(
    mean_predicted = mean(predicted),
    se = sd(predicted) / sqrt(n())
  )

p14 <- ggplot(predicted_by_variant, aes(x = campaign_variant, y = mean_predicted,
                                         fill = campaign_variant)) +
  geom_col(alpha = 0.7, color = "black") +
  geom_errorbar(aes(ymin = mean_predicted - 1.96*se, ymax = mean_predicted + 1.96*se),
                width = 0.2, size = 1) +
  geom_text(aes(label = paste0("$", round(mean_predicted, 2))), vjust = -2, size = 5) +
  scale_fill_manual(values = c("A" = "#E69F00", "B" = "#56B4E9", "C" = "#009E73")) +
  labs(
    title = "Model-Predicted Campaign Spend by Variant",
    subtitle = "Adjusted for customer characteristics (95% CI)",
    x = "Campaign Variant",
    y = "Predicted Campaign Spend ($)"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
ggsave("plots/14_predicted_spend_by_variant.png", p14, width = 10, height = 6)

# ===== SUMMARY =====

cat("\n\n===== KEY FINDINGS SUMMARY =====\n\n")

cat("QUESTION 1: What kinds of people make MORE purchases?\n")
cat("--------------------------------------------------------\n")
cat("Significant predictors (IRR > 1 increases purchases):\n\n")

significant_q1 <- coef_table %>%
  filter(`Pr(>|z|)` < 0.05, term != "(Intercept)") %>%
  arrange(`Pr(>|z|)`)

if(nrow(significant_q1) > 0) {
  for(i in 1:nrow(significant_q1)) {
    row <- significant_q1[i, ]
    direction <- ifelse(row$IRR > 1, "INCREASES", "DECREASES")
    pct_change <- abs((row$IRR - 1) * 100)
    cat(sprintf("• %s: IRR = %.3f (p < %.3f)\n", row$term, row$IRR, row$`Pr(>|z|)`))
    cat(sprintf("  → %s purchases by %.1f%%\n\n", direction, pct_change))
  }
}

cat("\nQUESTION 2: Which campaign variant should Company X use?\n")
cat("--------------------------------------------------------\n")
cat("Campaign Performance Summary:\n\n")

for(i in 1:nrow(variant_stats)) {
  row <- variant_stats[i, ]
  cat(sprintf("Variant %s: Mean = $%.2f (n = %d, Total = $%.2f)\n",
              row$campaign_variant, row$mean_spend, row$n, row$total_spend))
}

cat("\nStatistical Comparison (vs Variant A):\n")
if(nrow(variant_plot_data) > 0) {
  for(i in 1:nrow(variant_plot_data)) {
    row <- variant_plot_data[i, ]
    variant_name <- gsub("campaign_variant", "", row$term)
    direction <- ifelse(row$Estimate > 0, "MORE", "LESS")
    significance <- ifelse(row$`Pr(>|t|)` < 0.05, "SIGNIFICANT", "not significant")
    cat(sprintf("• Variant %s: $%.2f %s than A (p = %.4f) - %s\n",
                variant_name, abs(row$Estimate), direction, row$`Pr(>|t|)`, significance))
  }
}

cat("\n✓ All plots saved to 'plots/' directory\n")
cat("✓ Analysis complete!\n")