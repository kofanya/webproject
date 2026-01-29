from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, Ad, Review

admin_bp = Blueprint('admin_api', __name__)

def check_if_admin():
    claims = get_jwt()
    if not claims.get('is_administrator'):
        return {"error": "Вы не администратор"}, 403
    return None

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]

    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "is_admin": u.is_admin,
            "ads_count": len(u.ads)
        })
    return jsonify(result)

@admin_bp.route('/admin/users/<int:user_id>/make_admin', methods=['PUT'])
@jwt_required()
def make_user_admin(user_id):
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Пользователь не найден"}), 404

    user.is_admin = True
    db.session.commit()
    
    return jsonify({"message": f"Пользователь {user.name} теперь администратор"})


@admin_bp.route('/admin/ads', methods=['GET'])
@jwt_required()
def get_all_ads():
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]
    
    ads = Ad.query.all()
    result = []
    for ad in ads:
        result.append({
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "author_email": ad.author.email,
            "created_date": ad.created_date.isoformat()
        })
    return jsonify(result)

@admin_bp.route('/admin/ads/<int:ad_id>', methods=['DELETE'])
@jwt_required()
def delete_ad(ad_id):
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]

    ad = Ad.query.get(ad_id)
    if not ad:
        return jsonify({"message": "Объявление не найдено"}), 404

    db.session.delete(ad)
    db.session.commit()
    return jsonify({"message": "Объявление удалено"})

@admin_bp.route('/admin/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]

    try:
        reviews = Review.query.all()
        result = []
        for r in reviews:
            author_name = r.author.name if r.author else "Неизвестный автор"
            ad_title = "Объявление не указано"
            if r.ad_id:
                ad_info = Ad.query.get(r.ad_id)
                if ad_info: ad_title = ad_info.title
                else: ad_title = "Объявление удалено"
            result.append({
                "id": r.id,
                "text": r.text or "",
                "rating": r.rating,
                "author": author_name,     
                "ad_id": r.ad_id,
                "ad_title": ad_title  
            })
        return jsonify(result)

    except Exception as e:
        print(f"Error in get_reviews: {e}")
        return jsonify({"message": "Ошибка сервера", "error": str(e)}), 500

@admin_bp.route('/admin/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    error = check_if_admin()
    if error: return jsonify(error[0]), error[1]

    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Отзыв не найден"}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Отзыв удален"})