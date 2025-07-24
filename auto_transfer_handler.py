#!/usr/bin/env python3
"""
Auto Transfer Handler - Smart wallet management system
Enables automatic transfers between Spot, Margin, and Futures wallets
"""

import logging
from typing import Dict, Any, Optional, List

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

class AutoTransferHandler:
    def __init__(self, exchange_client):
        """Initialize auto transfer handler"""
        self.client = exchange_client
        self.min_transfer_amount = 1.0  # Minimum $1 USDT to transfer
        self.transfer_history = []
        
        logging.info("Auto Transfer Handler initialized")
    
    def check_and_transfer(self, target_wallet: str, required_amount: float) -> Dict[str, Any]:
        """
        Check wallet balance and transfer funds if needed
        
        Args:
            target_wallet (str): 'spot', 'margin', or 'futures'
            required_amount (float): Amount needed in USDT
            
        Returns:
            dict: Transfer result with success status
        """
        
        try:
            # Get current balances
            balances = self._get_all_wallet_balances()
            
            current_balance = balances.get(target_wallet, {}).get('USDT', 0)
            
            if current_balance >= required_amount:
                logging.info(f"✅ Sufficient balance in {target_wallet}: ${current_balance:.2f}")
                return {"success": True, "message": "Sufficient balance", "transferred": 0}
            
            # Calculate how much more we need
            needed_amount = required_amount - current_balance
            
            # Find source wallet with enough funds
            source_wallet = self._find_source_wallet(target_wallet, needed_amount, balances)
            
            if not source_wallet:
                logging.warning(f"❌ No wallet has enough funds for transfer")
                return {"success": False, "error": "Insufficient total funds"}
            
            # Execute transfer
            transfer_amount = min(needed_amount * 1.1, balances[source_wallet]['USDT'])  # Transfer 10% extra as buffer
            
            transfer_result = self._execute_transfer(
                source_wallet, 
                target_wallet, 
                transfer_amount
            )
            
            if transfer_result['success']:
                logging.info(f"✅ Transferred ${transfer_amount:.2f} from {source_wallet} to {target_wallet}")
                
                # Record transfer
                self.transfer_history.append({
                    'from': source_wallet,
                    'to': target_wallet,
                    'amount': transfer_amount,
                    'timestamp': transfer_result.get('timestamp'),
                    'reason': f"Required ${required_amount:.2f}"
                })
                
                return {
                    "success": True,
                    "transferred": transfer_amount,
                    "from_wallet": source_wallet,
                    "to_wallet": target_wallet
                }
            else:
                return transfer_result
                
        except Exception as e:
            logging.error(f"Auto transfer error: {e}")
            return {"success": False, "error": str(e)}
    
    def optimize_wallet_distribution(self) -> Dict[str, Any]:
        """
        Optimize fund distribution across wallets based on trading activity
        
        Returns:
            dict: Optimization result
        """
        
        try:
            balances = self._get_all_wallet_balances()
            total_usdt = sum(wallet.get('USDT', 0) for wallet in balances.values())
            
            if total_usdt < 10:
                logging.info("Total balance too low for optimization")
                return {"success": True, "message": "Balance too low for optimization"}
            
            # Optimal distribution (can be adjusted based on strategy)
            optimal_distribution = {
                'spot': 0.3,      # 30% in spot for base trading
                'futures': 0.5,   # 50% in futures for leveraged opportunities  
                'margin': 0.2     # 20% in margin for medium leverage trades
            }
            
            transfers_needed = []
            
            for wallet, target_ratio in optimal_distribution.items():
                current_amount = balances.get(wallet, {}).get('USDT', 0)
                target_amount = total_usdt * target_ratio
                difference = target_amount - current_amount
                
                if abs(difference) > 5:  # Only transfer if difference > $5
                    transfers_needed.append({
                        'wallet': wallet,
                        'current': current_amount,
                        'target': target_amount,
                        'difference': difference
                    })
            
            # Execute optimization transfers
            executed_transfers = []
            for transfer_data in transfers_needed:
                if transfer_data['difference'] > 0:  # Need to receive funds
                    source = self._find_source_wallet_for_optimization(
                        transfer_data['wallet'], 
                        transfer_data['difference'],
                        balances
                    )
                    
                    if source:
                        result = self._execute_transfer(
                            source, 
                            transfer_data['wallet'], 
                            transfer_data['difference']
                        )
                        
                        if result['success']:
                            executed_transfers.append({
                                'from': source,
                                'to': transfer_data['wallet'],
                                'amount': transfer_data['difference']
                            })
            
            logging.info(f"Wallet optimization completed: {len(executed_transfers)} transfers executed")
            
            return {
                "success": True,
                "transfers_executed": len(executed_transfers),
                "transfers": executed_transfers
            }
            
        except Exception as e:
            logging.error(f"Wallet optimization error: {e}")
            return {"success": False, "error": str(e)}
    
    def emergency_consolidation(self, target_wallet: str = 'futures') -> Dict[str, Any]:
        """
        Emergency consolidation of all funds to single wallet
        
        Args:
            target_wallet (str): Wallet to consolidate funds into
            
        Returns:
            dict: Consolidation result
        """
        
        try:
            balances = self._get_all_wallet_balances()
            total_consolidated = 0
            transfers = []
            
            for wallet, balance_info in balances.items():
                if wallet == target_wallet:
                    continue
                
                usdt_amount = balance_info.get('USDT', 0)
                
                if usdt_amount > self.min_transfer_amount:
                    result = self._execute_transfer(wallet, target_wallet, usdt_amount)
                    
                    if result['success']:
                        total_consolidated += usdt_amount
                        transfers.append({
                            'from': wallet,
                            'amount': usdt_amount
                        })
            
            logging.info(f"Emergency consolidation: ${total_consolidated:.2f} moved to {target_wallet}")
            
            return {
                "success": True,
                "total_consolidated": total_consolidated,
                "target_wallet": target_wallet,
                "transfers": transfers
            }
            
        except Exception as e:
            logging.error(f"Emergency consolidation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_all_wallet_balances(self) -> Dict[str, Dict[str, float]]:
        """Get balances from all wallet types"""
        all_balances = {}
        
        try:
            # Spot balance
            spot_balance = self.client.fetch_balance({'type': 'spot'})
            all_balances['spot'] = {'USDT': spot_balance.get('USDT', {}).get('free', 0)}
            
            # Futures balance  
            futures_balance = self.client.fetch_balance({'type': 'swap'})
            all_balances['futures'] = {'USDT': futures_balance.get('USDT', {}).get('free', 0)}
            
            # Margin balance
            margin_balance = self.client.fetch_balance({'type': 'margin'})
            all_balances['margin'] = {'USDT': margin_balance.get('USDT', {}).get('free', 0)}
            
            return all_balances
            
        except Exception as e:
            logging.error(f"Error getting wallet balances: {e}")
            return {}
    
    def _find_source_wallet(self, target_wallet: str, needed_amount: float, balances: Dict[str, Dict[str, float]]) -> Optional[str]:
        """Find wallet with sufficient funds for transfer"""
        
        # Priority order for source wallets
        wallet_priority = ['spot', 'futures', 'margin']
        
        # Remove target wallet from priority
        if target_wallet in wallet_priority:
            wallet_priority.remove(target_wallet)
        
        for wallet in wallet_priority:
            available = balances.get(wallet, {}).get('USDT', 0)
            if available >= needed_amount + self.min_transfer_amount:  # Keep minimum balance
                return wallet
        
        return None
    
    def _find_source_wallet_for_optimization(self, target_wallet: str, needed_amount: float, balances: Dict[str, Dict[str, float]]) -> Optional[str]:
        """Find source wallet for optimization transfers"""
        
        best_source = None
        max_excess = 0
        
        for wallet, balance_info in balances.items():
            if wallet == target_wallet:
                continue
            
            available = balance_info.get('USDT', 0)
            excess = available - (available * 0.1)  # Keep 10% buffer
            
            if excess >= needed_amount and excess > max_excess:
                max_excess = excess
                best_source = wallet
        
        return best_source
    
    def _execute_transfer(self, from_wallet: str, to_wallet: str, amount: float) -> Dict[str, Any]:
        """Execute transfer between wallets"""
        
        if amount < self.min_transfer_amount:
            return {"success": False, "error": "Amount too small"}
        
        try:
            # OKX transfer mapping
            wallet_mapping = {
                'spot': '18',      # Trading account
                'futures': '6',    # Futures account  
                'margin': '5'      # Margin account
            }
            
            from_id = wallet_mapping.get(from_wallet)
            to_id = wallet_mapping.get(to_wallet)
            
            if not from_id or not to_id:
                return {"success": False, "error": "Invalid wallet type"}
            
            # Execute transfer using OKX API
            transfer_result = self.client.transfer(
                code='USDT',
                amount=amount,
                fromAccount=from_id,
                toAccount=to_id
            )
            
            if transfer_result and transfer_result.get('id'):
                logging.info(f"Transfer executed: {from_wallet} → {to_wallet} ${amount:.2f}")
                
                return {
                    "success": True,
                    "transfer_id": transfer_result['id'],
                    "amount": amount,
                    "from": from_wallet,
                    "to": to_wallet,
                    "timestamp": transfer_result.get('timestamp')
                }
            else:
                return {"success": False, "error": "Transfer failed - no ID returned"}
                
        except ccxt.InsufficientFunds as e:
            logging.error(f"Insufficient funds for transfer: {e}")
            return {"success": False, "error": "Insufficient funds"}
        except Exception as e:
            logging.error(f"Transfer execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_transfer_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transfer history"""
        return self.transfer_history[-limit:] if self.transfer_history else []
    
    def get_wallet_summary(self) -> Dict[str, Any]:
        """Get comprehensive wallet summary"""
        try:
            balances = self._get_all_wallet_balances()
            
            total_usdt = sum(wallet.get('USDT', 0) for wallet in balances.values())
            
            summary = {
                'total_balance': total_usdt,
                'wallets': {},
                'distribution': {}
            }
            
            for wallet, balance_info in balances.items():
                usdt_amount = balance_info.get('USDT', 0)
                percentage = (usdt_amount / total_usdt * 100) if total_usdt > 0 else 0
                
                summary['wallets'][wallet] = {
                    'balance': usdt_amount,
                    'percentage': percentage
                }
            
            return summary
            
        except Exception as e:
            logging.error(f"Error getting wallet summary: {e}")
            return {'total_balance': 0, 'wallets': {}, 'distribution': {}}