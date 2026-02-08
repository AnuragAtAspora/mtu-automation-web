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
            )
        }
        
        return metrics
    
    @staticmethod
    def _calculate_country_metrics(campaign_data: Dict, user_counts: Dict, country: str) -> Dict:
        """Calculate metrics for a specific country"""
        
        # Get user counts
        total_users = user_counts.get(f'{country}_total_users', 0)
        active_users = user_counts.get(f'{country}_active_users', 0)
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
        pn_delivered = campaign_data.get('pn_delivered', 0)
        email_delivered = campaign_data.get('email_delivered', 0)
        pn_clicks = campaign_data.get('pn_clicks', 0)
        email_opens = campaign_data.get('email_opens', 0)
        pn_unsubscribes = campaign_data.get('pn_unsubscribes', 0)
        email_unsubscribes = campaign_data.get('email_unsubscribes', 0)
        
        # Calculate metrics
        metrics = {
            # Communications per user
            'tx_pn_per_user': round(tx_pn_sent / active_users, 4) if active_users > 0 else 0,
            'tx_email_per_user': round(tx_email_sent / active_users, 4) if active_users > 0 else 0,
            'pr_pn_per_user': round(pr_pn_sent / total_users, 4) if total_users > 0 else 0,
            'pr_email_per_user': round(pr_email_sent / total_users, 4) if total_users > 0 else 0,
            
            # MTU (Monthly Transacting Users who received comms)
            'push_mtu': round((push_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            'email_mtu': round((email_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            
            # Delivery rates
            'push_delivery_rate': round((pn_delivered / (tx_pn_sent + pr_pn_sent)) * 100, 2) if (tx_pn_sent + pr_pn_sent) > 0 else 0,
            'email_delivery_rate': round((email_delivered / (tx_email_sent + pr_email_sent)) * 100, 2) if (tx_email_sent + pr_email_sent) > 0 else 0,
            
            # Engagement rates
            'push_ctr': round((pn_clicks / pn_delivered) * 100, 2) if pn_delivered > 0 else 0,
            'email_open_rate': round((email_opens / email_delivered) * 100, 2) if email_delivered > 0 else 0,
            
            # Unsubscribe rates
            'push_unsub_rate': round((pn_unsubscribes / pn_delivered) * 100, 4) if pn_delivered > 0 else 0,
            'email_unsub_rate': round((email_unsubscribes / email_delivered) * 100, 4) if email_delivered > 0 else 0,
            
            # Raw counts for reference
            'total_users': total_users,
            'active_users': active_users,
            'push_received': push_received,
            'email_received': email_received,
            'push_received_active': push_received_active,
            'email_received_active': email_received_active
        }
        
        return metrics
    
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
            'pn_delivered': (
                aggregated_metrics.get('uk_transactional_push', {}).get('delivered', 0) +
                aggregated_metrics.get('uk_promotional_push', {}).get('delivered', 0)
            ),
            'email_delivered': (
                aggregated_metrics.get('uk_transactional_email', {}).get('delivered', 0) +
                aggregated_metrics.get('uk_promotional_email', {}).get('delivered', 0)
            ),
            'pn_clicks': (
                aggregated_metrics.get('uk_transactional_push', {}).get('click', 0) +
                aggregated_metrics.get('uk_promotional_push', {}).get('click', 0)
            ),
            'email_opens': (
                aggregated_metrics.get('uk_transactional_email', {}).get('open', 0) +
                aggregated_metrics.get('uk_promotional_email', {}).get('open', 0)
            ),
            'pn_unsubscribes': (
                aggregated_metrics.get('uk_transactional_push', {}).get('unsubscribe', 0) +
                aggregated_metrics.get('uk_promotional_push', {}).get('unsubscribe', 0)
            ),
            'email_unsubscribes': (
                aggregated_metrics.get('uk_transactional_email', {}).get('unsubscribe', 0) +
                aggregated_metrics.get('uk_promotional_email', {}).get('unsubscribe', 0)
            )
        }
        
        uae_data = {
            'tx_pn_sent': aggregated_metrics.get('uae_transactional_push', {}).get('sent', 0),
            'tx_email_sent': aggregated_metrics.get('uae_transactional_email', {}).get('sent', 0),
            'pr_pn_sent': aggregated_metrics.get('uae_promotional_push', {}).get('sent', 0),
            'pr_email_sent': aggregated_metrics.get('uae_promotional_email', {}).get('sent', 0),
            'pn_delivered': (
                aggregated_metrics.get('uae_transactional_push', {}).get('delivered', 0) +
                aggregated_metrics.get('uae_promotional_push', {}).get('delivered', 0)
            ),
            'email_delivered': (
                aggregated_metrics.get('uae_transactional_email', {}).get('delivered', 0) +
                aggregated_metrics.get('uae_promotional_email', {}).get('delivered', 0)
            ),
            'pn_clicks': (
                aggregated_metrics.get('uae_transactional_push', {}).get('click', 0) +
                aggregated_metrics.get('uae_promotional_push', {}).get('click', 0)
            ),
            'email_opens': (
                aggregated_metrics.get('uae_transactional_email', {}).get('open', 0) +
                aggregated_metrics.get('uae_promotional_email', {}).get('open', 0)
            ),
            'pn_unsubscribes': (
                aggregated_metrics.get('uae_transactional_push', {}).get('unsubscribe', 0) +
                aggregated_metrics.get('uae_promotional_push', {}).get('unsubscribe', 0)
            ),
            'email_unsubscribes': (
                aggregated_metrics.get('uae_transactional_email', {}).get('unsubscribe', 0) +
                aggregated_metrics.get('uae_promotional_email', {}).get('unsubscribe', 0)
            )
        }
        
        return {
            'uk': uk_data,
            'uae': uae_data
        }
