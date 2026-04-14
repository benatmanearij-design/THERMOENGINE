# backend/thermo_engine/activity_models.py
import numpy as np
from db import get_db

# =========================
# NRTL
# =========================
class NRTL:
    def get_gamma(self, x, T, a12, a21, alpha):

        x1, x2 = x

        tau12 = a12 / T
        tau21 = a21 / T

        G12 = np.exp(-alpha * tau12)
        G21 = np.exp(-alpha * tau21)

        gamma1 = np.exp(
            x2**2 * (
                tau21 * (G21 / (x1 + x2 * G21))**2 +
                tau12 * G12 / (x2 + x1 * G12)**2
            )
        )

        gamma2 = np.exp(
            x1**2 * (
                tau12 * (G12 / (x2 + x1 * G12))**2 +
                tau21 * G21 / (x1 + x2 * G21)**2
            )
        )

        return [gamma1, gamma2]


# =========================
# UNIQUAC (simplifié)
# =========================
class UNIQUAC:
    def get_gamma(self, x, r, q):

        phi = (r * x) / np.sum(r * x)
        theta = (q * x) / np.sum(q * x)

        gamma = np.exp(np.log(phi / x))
        return gamma


# =========================
# UNIFAC 🔥 (corrigé et stable)
# =========================
class UNIFAC:

    def get_groups(self, component_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT g.id, g.R, g.Q, cg.count
            FROM component_groups cg
            JOIN unifac_groups g ON g.id = cg.group_id
            WHERE cg.component_id = %s
        """, (component_id,))

        data = cursor.fetchall()

        cursor.close()
        db.close()

        return data

    def get_interaction(self, g1, g2):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT Aij FROM unifac_interactions
            WHERE group1=%s AND group2=%s
        """, (g1, g2))

        result = cursor.fetchone()

        cursor.close()
        db.close()

        return result[0] if result else 0

    def get_gamma(self, comp_ids, x, T):

        ln_gamma = []

        # récupération groupes pour tous composants
        all_groups = [self.get_groups(cid) for cid in comp_ids]

        for i, groups_i in enumerate(all_groups):

            ln_gamma_i = 0

            for (gk, Rk, Qk, vk) in groups_i:

                denom = 0

                for j, groups_j in enumerate(all_groups):
                    for (gm, Rm, Qm, vm) in groups_j:

                        A = self.get_interaction(gk, gm)
                        denom += x[j] * vm * np.exp(-A / T)

                if denom <= 0:
                    denom = 1e-6

                ln_gamma_i += vk * (-np.log(denom))

            ln_gamma.append(ln_gamma_i)

        return np.exp(ln_gamma)