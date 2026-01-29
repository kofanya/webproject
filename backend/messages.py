from flask import Blueprint, jsonify, request, g
from models import Message, Ad, User, db
from sqlalchemy import or_, and_, desc

api_messages_bp = Blueprint('api_messages', __name__)

@api_messages_bp.route('/messages', methods=['POST'])
def send_message():
    user_id = g.current_user_id
    if not user_id:
        return jsonify({'error': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    ad_id = data.get('ad_id')
    recipient_id = data.get('recipient_id')
    body = data.get('body', '').strip()

    if not ad_id or not body:
        return jsonify({'error': 'ad_id и текст сообщения обязательны'}), 400

    ad = Ad.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404
    if not recipient_id:
        if ad.user_id == user_id:
             return jsonify({'error': 'Автор объявления должен указать получателя (покупателя) при ответе'}), 400
        recipient_id = ad.user_id
    else:
        recipient_id = int(recipient_id)
        if recipient_id == user_id:
            return jsonify({'error': 'Нельзя писать самому себе'}), 400

    try:
        new_msg = Message(
            body=body,
            sender_id=user_id,
            recipient_id=recipient_id,
            ad_id=ad_id
        )
        db.session.add(new_msg)
        db.session.commit()
        
        return jsonify({
            'message': 'Сообщение отправлено',
            'data': {
                'id': new_msg.id,
                'body': new_msg.body,
                'created_date': new_msg.created_date.isoformat(),
                'sender_id': user_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при отправке', 'details': str(e)}), 500

@api_messages_bp.route('/chats', methods=['GET'])
def get_my_chats():
    user_id = g.current_user_id
    if not user_id:
        return jsonify({'error': 'Необходима авторизация'}), 401

    messages = Message.query.filter(
        or_(Message.sender_id == user_id, Message.recipient_id == user_id)
    ).order_by(Message.created_date.desc()).all()

    chats = {}
    
    for msg in messages:
        partner_id = msg.recipient_id if msg.sender_id == user_id else msg.sender_id
        
        chat_key = f"{msg.ad_id}_{partner_id}"
        if chat_key not in chats:
            partner = User.query.get(partner_id)
            ad = Ad.query.get(msg.ad_id)
            
            if partner and ad:
                chats[chat_key] = {
                    'ad_id': ad.id,
                    'ad_title': ad.title,
                    'ad_photo': ad.photos[0].image_filename if ad.photos else None,
                    'partner_id': partner.id,
                    'partner_name': f"{partner.name} {partner.last_name}",
                    'last_message': msg.body,
                    'last_message_date': msg.created_date.isoformat(),
                    'is_my_ad': ad.user_id == user_id 
                }

    return jsonify(list(chats.values()))

@api_messages_bp.route('/chats/<int:ad_id>/<int:partner_id>', methods=['GET'])
def get_conversation(ad_id, partner_id):
    user_id = g.current_user_id
    if not user_id:
        return jsonify({'error': 'Необходима авторизация'}), 401
    messages = Message.query.filter(
        and_(
            Message.ad_id == ad_id,
            or_(
                and_(Message.sender_id == user_id, Message.recipient_id == partner_id),
                and_(Message.sender_id == partner_id, Message.recipient_id == user_id)
            )
        )
    ).order_by(Message.created_date.asc()).all() 

    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'body': msg.body,
            'sender_id': msg.sender_id,
            'recipient_id': msg.recipient_id,
            'created_date': msg.created_date.isoformat(),
            'is_mine': msg.sender_id == user_id 
        })

    return jsonify(result)

@api_messages_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    user_id = g.current_user_id
    if not user_id:
        return jsonify({'error': 'Необходима авторизация'}), 401

    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({'error': 'Сообщение не найдено'}), 404

    if msg.sender_id != user_id:
        return jsonify({'error': 'Вы не можете удалить чужое сообщение'}), 403

    try:
        db.session.delete(msg)
        db.session.commit()
        return jsonify({'message': 'Сообщение удалено'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка удаления', 'details': str(e)}), 500