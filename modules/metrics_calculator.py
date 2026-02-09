"""
Module for calculating communication metrics
"""
from typing import Dict


class MetricsCalculator:
    """Calculate communication metrics from campaign data and user counts"""
    
    @staticmethod
    def calculate_metrics(campaign_data: Dict, user_counts: Dict) -> Dict:
        """
        Calculate all metrics for UK and UAE
        
        Args:
            campaign_data: Dict with UK and UAE campaign metrics
            user_counts: Dict with segment counts
            
        Returns:
            Dict with calculated metrics for UK and UAE
        """
        metrics = {
            'uk': MetricsCalculator._calculate_country_metrics(
                campaign_data.get('uk', {}),
                user_counts,
                'uk'
            ),
            'uae': MetricsCalculator._calculate_country_metrics(
                campaign_data.get('uae', {}),
                user_counts,
                'uae'
            ),
            'combined': MetricsCalculator._calculate_combined_metrics(
                campaign_data,
                user_counts
            )
        }
        
        return metrics
    
    @staticmethod
    def _calculate_country_metrics(campaign_data: Dict, user_counts: Dict, country: str) -> Dict:
        """Calculate metrics for a specific country"""
        
        # Get user counts
        total_users = user_counts.get(f'{country}_total_users', 0)
        active_users = user_counts.get(f'{country}_active_users', 0)
        transacted_users = user_counts.get(f'{country}_transacted_users', 0)
        push_received = user_counts.get(f'{country}_push_received', 0)
        email_received = user_counts.get(f'{country}_email_received', 0)
        push_received_active = user_counts.get(f'{country}_push_received_active', 0)
        email_received_active = user_counts.get(f'{country}_email_received_active', 0)
        push_unsubscribed = user_counts.get(f'{country}_push_unsubscribed', 0)
        email_unsubscribed = user_counts.get(f'{country}_email_unsubscribed', 0)
        
        # Get campaign data
        tx_pn_sent = campaign_data.get('tx_pn_sent', 0)
        tx_email_sent = campaign_data.get('tx_email_sent', 0)
        pr_pn_sent = campaign_data.get('pr_pn_sent', 0)
        pr_email_sent = campaign_data.get('pr_email_sent', 0)
        pn_clicks = campaign_data.get('pn_clicks', 0)
        email_opens = campaign_data.get('email_opens', 0)
        total_pn_sent = tx_pn_sent + pr_pn_sent
        total_email_sent = tx_email_sent + pr_email_sent
        
        # Calculate metrics based on confirmed formulas
        metrics = {
            # 1. % receiving comms (total userbase)
            'pct_receiving_pn_total': round((push_received / total_users) * 100, 2) if total_users > 0 else 0,
            'pct_receiving_email_total': round((email_received / total_users) * 100, 2) if total_users > 0 else 0,
            
            # 2. Unsubscribe rate (denominator: total users)
            'unsub_rate_pn': round((push_unsubscribed / total_users) * 100, 2) if total_users > 0 else 0,
            'unsub_rate_email': round((email_unsubscribed / total_users) * 100, 2) if total_users > 0 else 0,
            
            # 3. % receiving comms (active userbase)
            'pct_receiving_pn_active': round((push_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            'pct_receiving_email_active': round((email_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            
            # 4. No. of comms received per user
            'comms_per_user_tx_pn': round(tx_pn_sent / transacted_users, 2) if transacted_users > 0 else 0,
            'comms_per_user_tx_email': round(tx_email_sent / transacted_users, 2) if transacted_users > 0 else 0,
            'comms_per_user_pr_pn': round(pr_pn_sent / total_users, 2) if total_users > 0 else 0,
            'comms_per_user_pr_email': round(pr_email_sent / total_users, 2) if total_users > 0 else 0,
            
            # 5. PN CTR
            'pn_ctr': round((pn_clicks / total_pn_sent) * 100, 2) if total_pn_sent > 0 else 0,
            
            # 6. Email Open Rate
            'email_open_rate': round((email_opens / total_email_sent) * 100, 2) if total_email_sent > 0 else 0,
            
            # Raw counts for reference
            'total_users': total_users,
            'active_users': active_users,
            'transacted_users': transacted_users,
            'push_received': push_received,
            'email_received': email_received,
            'push_received_active': push_received_active,
            'email_received_active': email_received_active,
            'push_unsubscribed': push_unsubscribed,
            'email_unsubscribed': email_unsubscribed,
            'tx_pn_sent': tx_pn_sent,
            'tx_email_sent': tx_email_sent,
            'pr_pn_sent': pr_pn_sent,
            'pr_email_sent': pr_email_sent,
            'pn_clicks': pn_clicks,
            'email_opens': email_opens
        }
        
        return metrics
    
    @staticmethod
    def _calculate_combined_metrics(campaign_data: Dict, user_counts: Dict) -> Dict:
        """Calculate combined metrics (for reference/comparison)"""
        uk_data = campaign_data.get('uk', {})
        uae_data = campaign_data.get('uae', {})
        
        # Combined totals
        total_pn_sent = (uk_data.get('tx_pn_sent', 0) + uk_data.get('pr_pn_sent', 0) + 
                        uae_data.get('tx_pn_sent', 0) + uae_data.get('pr_pn_sent', 0))
        total_email_sent = (uk_data.get('tx_email_sent', 0) + uk_data.get('pr_email_sent', 0) + 
                           uae_data.get('tx_email_sent', 0) + uae_data.get('pr_email_sent', 0))
        total_pn_clicks = uk_data.get('pn_clicks', 0) + uae_data.get('pn_clicks', 0)
        total_email_opens = uk_data.get('email_opens', 0) + uae_data.get('email_opens', 0)
        
        return {
            'total_pn_sent': total_pn_sent,
            'total_email_sent': total_email_sent,
            'total_pn_clicks': total_pn_clicks,
            'total_email_opens': total_email_opens
        }
    
    @staticmethod
    def prepare_campaign_data_for_calculation(categories: Dict, aggregated_metrics: Dict) -> Dict:
        """
        Prepare campaign data in format needed for metrics calculation
        
        Args:
            categories: Campaigns grouped by 8 categories
            aggregated_metrics: Aggregated metrics for each category
            
        Returns:
            Dict with UK and UAE campaign data
        """
        uk_data = {
            'tx_pn_sent': aggregated_metrics.get('uk_transactional_push', {}).get('sent', 0),
            'tx_email_sent': aggregated_metrics.get('uk_transactional_email', {}).get('sent', 0),
            'pr_pn_sent': aggregated_metrics.get('uk_promotional_push', {}).get('sent', 0),
            'pr_email_sent': aggregated_metrics.get('uk_promotional_email', {}).get('sent', 0),
            'pn_clicks': (
                aggregated_metrics.get('uk_transactional_push', {}).get('click', 0) +
                aggregated_metrics.get('uk_promotional_push', {}).get('click', 0)
            ),
            'email_opens': (
                aggregated_metrics.get('uk_transactional_email', {}).get('open', 0) +
                aggregated_metrics.get('uk_promotional_email', {}).get('open', 0)
            )
        }
        
        uae_data = {
            'tx_pn_sent': aggregated_metrics.get('uae_transactional_push', {}).get('sent', 0),
            'tx_email_sent': aggregated_metrics.get('uae_transactional_email', {}).get('sent', 0),
            'pr_pn_sent': aggregated_metrics.get('uae_promotional_push', {}).get('sent', 0),
            'pr_email_sent': aggregated_metrics.get('uae_promotional_email', {}).get('sent', 0),
            'pn_clicks': (
                aggregated_metrics.get('uae_transactional_push', {}).get('click', 0) +
                aggregated_metrics.get('uae_promotional_push', {}).get('click', 0)
            ),
            'email_opens': (
                aggregated_metrics.get('uae_transactional_email', {}).get('open', 0) +
                aggregated_metrics.get('uae_promotional_email', {}).get('open', 0)
            )
        }
        
        return {
            'uk': uk_data,
            'uae': uae_data
        }
